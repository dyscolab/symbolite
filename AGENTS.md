# AGENTS.md — symbolite

Instructions for coding agents working **on** this repository. The user-facing
introduction is in [README.md](README.md). Record user-visible changes in
[CHANGES](CHANGES) under "Unreleased".

## Project overview

symbolite is a minimal symbolic-expression library. Users build expressions
with Python operators on `Symbol`, `Real`, `Vector` and `Boolean`. The
expressions stay symbolic until `translate(expr, libsl)` hands them to a
backend module: libstd, libnumpy, libjax, libnumba or libsympy to compute
values, libpythoncode or liblatex to generate code or LaTeX.

It deliberately does **not** simplify, differentiate, or evaluate eagerly.
SymPy is only one backend among several.

symbolite is the base of the Dyscolab stack. poincare builds on it, and
simbio and jablonski build on poincare. Typical tasks are adding or fixing a
mathematical operation in every backend, fixing traversal, substitution or
translation semantics, and changing code generation for `Block`s.

## Repository map

| Path | Responsibility | Touch when |
| --- | --- | --- |
| `src/symbolite/core/` | `SymboliteObject`, `Value`, `Call`, `Function`/`Operator`/`UserFunction`, `Assign`/`Block`, `Unsupported` | Changing object identity, naming, call representation, block validation |
| `src/symbolite/abstract/` | Public symbolic types and the *declarations* of every operation (`real.py`, `vector.py`, `boolean.py`, `symbol.py`, `lang.py`) | Adding or changing an operation's signature, arity, precedence, output type |
| `src/symbolite/impl/lib*/` | One package per backend, with a module per abstract namespace (`real`, `vector`, `boolean`, `symbol`, `lang`) | Implementing an operation for a backend |
| `src/symbolite/impl/__init__.py` | `Kind` (VALUE/CODE), backend discovery `get_all_implementations` | Adding a backend or optional dependency |
| `src/symbolite/impl/_lang_value_utils.py` | Compiles generated Python source for numerical `Block`s | Block compilation |
| `src/symbolite/ops/` | `translate`, `substitute`, `as_code`, `yield_named`, `tree_view`, `traversal` (`Layer`, `fold`, `rewrite`, `transform`, `walk`), `_dispatch.py` | Changing generic algorithms over expressions |
| `src/symbolite/testsuite/` | The whole test suite (this is the only `testpaths` entry) | Always |

## Architecture and core abstractions

- **Opaque value objects.** Every symbolic object stores its state in one
  `NamedTuple` in `__symbolite_info__`, read and written through
  `get_symbolite_info` and `set_symbolite_info`
  ([core/symbolite_object.py](src/symbolite/core/symbolite_object.py)).
  `==` and `hash` compare that info *structurally* and return `bool`.
- **Values.** `Value(name_or_value)` holds a `Name(name, namespace)`, a `Call`,
  or a plain Python value. `"ns.name"` strings create namespaced (library)
  values such as `real.pi`. An empty string creates an anonymous value that
  `__set_name__` can rename until it has been hashed.
- **Functions and operators.** `abstract/*.py` declares each operation as a
  `Function`/`Operator` instance with `name`, `namespace`, arity, `output_type`
  and, for operators, `fmt` and `precedence`. Calling one returns
  `output_type(Call(...))`. Nothing is computed at that point.
- **Translation by name.** `ops/_translate.py` resolves each operation as
  `getattr(libsl, f"{namespace}.{name}")`. A non-namespaced value resolves to
  `libsl.<module>.<ClassName>(name)`. When the attribute is missing or is set
  to `Unsupported`, translation raises `symbolite.core.Unsupported`, a
  `ValueError`. Backend modules must therefore mirror the abstract namespaces
  and names exactly.
- **Backend kinds.** `KIND = Kind.VALUE` backends evaluate (numerical
  backends and libsympy). `Kind.CODE` backends (libpythoncode, liblatex) emit
  source. Numerical `Block` translation generates Python with libpythoncode
  and compiles it against the target backend, and libnumba then `njit`s the
  result. `UserFunction` needs an explicitly registered implementation for
  CODE backends.
- **Traversal.** `translate`, `substitute`, `yield_named` and `tree_view` are
  built on the iterative, explicit-stack traversal in `ops/_traversal.py`
  (`project`/`rebuild` adapters, `fold`). Operation overrides are
  `functools.singledispatch` registrations routed through `TraversalDispatch`.
- **Statements.** `Assign(lhs, rhs)` and `Block(inputs, outputs, lines, name=)`
  describe computations. Dependencies are validated at construction and again
  at translation.

## Invariants and constraints

Verified (by implementation or tests):

- **Do not evaluate symbolic values implicitly.** `Value.__bool__` raises
  `TypeError`. `==`/`!=` stay structural, and mathematical (in)equality is
  `.eq()`/`.ne()` (`test_truthiness.py`, `test_value_identity.py`). Making
  `==` symbolic breaks dict keys and hashing in every downstream package.
- **Every backend defines every declared name**, as a real implementation or
  as `= Unsupported`. `test_real_impls.py::test_is_defined` and
  `test_backend_contracts.py` enforce this for `real`, `vector` and `boolean`.
- **Numerical backends agree.** `test_real_impls.py::test_compare` checks them
  against `math`/builtins, and `test_backend_contracts.py` checks that direct
  translation and compiled `Block` execution give the same result.
- **Backend discovery hides only missing optional root dependencies** (numpy,
  jax, sympy, numba). Any other import error must propagate
  (`test_implementations.py`). Do not wrap backend imports in broad
  `try/except`.
- **Substitution is simultaneous and keeps identity.** Unchanged branches
  keep their identity, and new built-in containers are returned
  (`test_traversal.py`, `test_statement_traversal.py`).
- **Names cannot change after hashing** ([core/value.py](src/symbolite/core/value.py)).
- **Objects are pickleable** (`test_serialize.py`).
- **Operator precedence and `fmt` drive the text output** of `as_code`,
  libpythoncode and liblatex (`test_operator_precedence.py`, `test_pythoncode.py`,
  `test_liblatex.py`).

Established conventions:

- Traverse iteratively. Deep expressions must not hit the recursion limit (see
  CHANGES). Do not add recursive walkers to `ops/`.
- Operation semantics follow Python `math`/`operator` (for example `fmod`
  keeps the sign of the dividend, also in SymPy). Do not quietly switch
  backends to NumPy or SymPy conventions.
- Raise `Unsupported` when a backend lacks a capability. Do not emulate it
  with different semantics.
- Static result types are checked with `pytest-mypy-testing`
  (`@pytest.mark.mypy_testing` in `test_symbol.py`, `test_real_function.py`,
  `test_vector.py`).

Unresolved (ask a maintainer, do not decide):

- Which `symbolite.core`/`symbolite.impl` internals count as public. poincare
  and simbio use several of them (see Ecosystem compatibility).
- libnumba is not covered by CI: numba is absent from this repo's pixi
  environments, so discovery skips libnumba both locally and in CI.

## Development environment and commands

The manifest is [pixi.toml](pixi.toml). The default environment includes the
`py312`, `test`, `lint` and `build` features. `py313` and `py314` are
test-only.

```bash
pixi run test                      # pytest --doctest-modules -n auto
pixi run -e py314 test             # other Python versions, as in CI
pixi run test src/symbolite/testsuite/test_vector.py::test_name   # single test
pixi run lint                      # prek run --all-files (ruff check --fix, ruff format, mdformat, tombi)
pixi run build                     # uv build
```

- CI ([.github/workflows/ci.yml](.github/workflows/ci.yml)) imports libstd,
  libnumpy, libsympy and libjax, then runs lint, test and build.
- `pixi run lint` **rewrites files**. The tree currently has unformatted files
  and one ruff finding. Lint only the files you changed
  (`pixi run ruff check <files>`, `pixi run ruff format <files>`) unless a
  repo-wide reformat is requested.
- There is no standalone type-check task. The mypy typing tests run inside
  `pixi run test`.
- `conftest.py` README extraction is disabled (`setup_test_readme` returns
  immediately), so README examples are **not** tested. Check by hand any
  README example you edit.

Before calling a change done, run `pixi run test`, run ruff on the changed
files, and run the downstream test suites (see Ecosystem compatibility).

## Making changes

- **New operation:** declare it in `abstract/<ns>.py` with the right
  `Function`/`Operator` subclass, arity, `output_type`, and for operators
  `fmt` and `precedence`. Add it to `impl/lib*/<ns>.py` for **every**
  backend, or set it to `Unsupported`. Add it to the name and value tables
  in `test_real_impls.py`, or to the operation sets in
  `test_backend_contracts.py` for vector or boolean operations. Check its
  rendering in libpythoncode and liblatex.
- **Fixing a backend:** compare the behaviour against `math` and the other
  backends first. Fix it in the backend module, not with special cases in
  `ops/`.
- **New backend:** create `impl/libX/` with `KIND` and the `real`, `vector`,
  `boolean`, `symbol` and `lang` modules. If it needs an optional library,
  add that library to `_OPTIONAL_DEPENDENCIES`.
- **Traversal, substitute or translate:** start with `ops/_traversal.py` and
  `ops/_dispatch.py`. Keep singledispatch override precedence and the parent
  delegation behaviour, and run `test_traversal.py`,
  `test_statement_traversal.py` and `test_translate.py`.
- **Block/codegen:** the files involved are `core/lang.py`,
  `impl/libpythoncode/`, `impl/_lang_value_utils.py` and the `lang.py` of
  each numerical backend. poincare compiles every ODE right-hand side
  through this path.
- Fix bugs narrowly. CHANGES records many deliberate edge-case semantics, so
  read the related CHANGES entries before you "simplify" behaviour.

## Testing and scientific correctness

- Put tests in `src/symbolite/testsuite/test_<area>.py`. Parametrize over
  `get_all_implementations()` so that every installed backend is exercised.
- Missing optional backends are skipped through discovery or with
  `pytest.importorskip`. Do not skip for any other reason.
- Numerical agreement uses small explicit thresholds (`almost_equal`,
  threshold `1e-4`, in `test_real_impls.py`). Handle NaN and Inf explicitly.
  Doctests use `NUMBER`.
- Check new mathematical behaviour against an independent reference
  (`math`, SymPy, or a hand-derived value), not against the output of
  another symbolite backend alone.
- Do not weaken assertions, delete tests, widen thresholds, or turn
  failures into `Unsupported` to make tests pass.

## Ecosystem compatibility

Downstream code depends on more than the top-level API. poincare,
simbio and jablonski import, among others:

- `symbolite.ops.{translate, substitute, yield_named, count_named, get_name}`,
  with `translate.register(...)` for their own node types
- `symbolite.core.value.{Value, Name, ValueInfo}`, `symbolite.core.call.{Call, CallInfo}`
  (structural pattern matching in `poincare/reactions/reactions.py`),
  `symbolite.core.function.{Operator, BinaryOperator}`, `symbolite.core.Unsupported`
- `symbolite.impl.{libstd, libnumpy, libnumba, libjax, liblatex, Kind}` and
  the private `symbolite.impl._lang_value_utils.compile` (`poincare/compile.py`)
- `symbolite.abstract.lang.{Assign, Block}`, `symbolite.vector`, `symbolite.real`

**Run the downstream test suites for every change**, not only for changes to
the interfaces listed above. Internal refactors and bug fixes can break
downstream code in unexpected ways, through traversal order, identity,
hashing or code generation.

- The downstream repos are https://github.com/dyscolab/poincare,
  https://github.com/dyscolab/simbio and https://github.com/dyscolab/jablonski.
- Run their tests in an environment where **this checkout** of symbolite is
  installed from source. Their own pixi environments install the published
  symbolite, so they do not test your change.
- Before changing anything listed above, also search the downstream sources
  for uses (`rg "symbolite\." <repo>/src`).
- If you cannot run the downstream suites, say so explicitly in your
  report. Do not claim compatibility.

Keep changes backward compatible unless told otherwise, and document any
breaking change and its migration in CHANGES.

## Documentation and public API

- The public surface is `symbolite.__all__`, plus `symbolite.abstract`,
  `symbolite.impl` and `symbolite.ops`.
- Type every public signature. Operator return types are part of the
  contract and are tested with mypy.
- Give public functions docstrings in NumPy style (Parameters/Notes). Keep
  doctests runnable, since `--doctest-modules` is on.
- Update README.md when user-facing behaviour changes, and CHANGES for every
  user-visible change.

## Completion checklist

- [ ] Read the abstract declaration and **all** backend implementations of anything you changed.
- [ ] No implicit evaluation, no symbolic `==`, and identity and pickling are preserved.
- [ ] Every backend defines the name or marks it `Unsupported`, and the parity tables are updated.
- [ ] `pixi run test` passes, and ruff is clean on the changed files.
- [ ] poincare, simbio and jablonski tests pass against this checkout (for every change), or the user is told they were not run.
- [ ] CHANGES updated, and unverified assumptions reported to the user.
