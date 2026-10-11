![Package](https://img.shields.io/pypi/v/symbolite?label=symbolite)
![CodeStyle](https://img.shields.io/badge/code%20style-black-000000.svg)
![License](https://img.shields.io/pypi/l/symbolite?label=license)
![PyVersion](https://img.shields.io/pypi/pyversions/symbolite?label=python)
[![CI](https://github.com/dyscolab/symbolite/actions/workflows/ci.yml/badge.svg)](https://github.com/dyscolab/symbolite/actions/workflows/ci.yml)
[![Lint](https://github.com/dyscolab/symbolite/actions/workflows/lint.yml/badge.svg)](https://github.com/dyscolab/symbolite/actions/workflows/lint.yml)

# symbolite: a minimalistic symbolic python package

______________________________________________________________________

Symbolite allows you to create symbolic mathematical
expressions. Just create a symbol (or more) and operate with them as you
will normally do in Python.

```python
>>> from symbolite import Symbol, substitute, translate
>>> x = Symbol("x")
>>> y = Symbol("y")
>>> expr1 = x + 3 * y
>>> print(expr1)
x + 3 * y
```

An expression is just an unnamed Symbol.
You can easily replace the symbols by the desired value.

```python
>>> expr2 = substitute(expr1, {x: 5, y: 2})
>>> print(expr2)
5 + 3 * 2
```

The output is still a symbolic expression, which you can translate:

```python
>>> translate(expr2)
11
```

Notice that we also got a warning (`No libsl provided, defaulting to Python standard library.`).
This is because translating an expression requires an actual library implementation,
named usually as `libsl`. The default one just uses python's math module.

You can avoid this warning by explicitely providing an `libsl` implementation.

```python
>>> from symbolite.impl import libstd
>>> translate(expr2, libstd)
11
```

You can also import it with the right name and it will be found

```python
>>> from symbolite.impl import libstd as libsl
>>> translate(expr2)
11
```

In addition to the `Symbol` class, there is also a `Scalar` and `Vector` classes
to represent integer, floats or complex numbers, and an array of those.

```python
>>> from symbolite import real, Vector
>>> x = Scalar("x")
>>> y = Scalar("y")
>>> v = Vector("v")
>>> expr1 = x + 3 * y
>>> print(expr1)
x + 3 * y
>>> print(2 * v)
2 * v
```

Mathematical functions that operate on scalars are available in the `scalar` module.

```python
>>> from symbolite import real
>>> expr3 = 3. * scalar.cos(0.5)
>>> print(expr3)
3.0 * scalar.cos(0.5)
```

Mathematical functions that operate on vectors are available in the `vector` module.

```python
>>> from symbolite import vector
>>> expr4 = 3. * vector.sum((1, 2, 3))
>>> print(expr4)
3.0 * vector.sum((1, 2, 3))
```

Notice that functions are named according to the python math module.
Again, this is a symbolic expression until translated.

```python
>>> translate(expr3)
2.6327476856711
>>> translate(expr4)
18.0
```

Three other implementations are provided:
[NumPy](https://numpy.org/),
[SymPy](https://www.sympy.org),
[JAX](https://jax.readthedocs.io).

```python
>>> from symbolite.impl import libnumpy
>>> translate(expr3, libsl=libnumpy)
np.float64(2.6327476856711183)
>>> from symbolite.impl import libsympy
>>> translate(expr3, libsl=libsympy)
2.6327476856711
```

(notice that the way that the different libraries round and
display may vary)

In general, all symbols must be replaced by values in order
to translate an expression. However, when using an implementation
like SymPy that contains a Scalar object you can still translate.

```python
>>> from symbolite.impl import libsympy as libsl
>>> translate(3. * scalar.cos(x), libsl)
3.0*cos(x)
```

which is actually a SymPy expression with a SymPy symbol (`x`).

SymPy translation preserves `Real` symbols' real-valued assumptions. It converts
`Assign` to a SymPy `Assignment` and `Block` to a `FunctionDefinition` AST, not a
Python callable. Block outputs retain their declared order; a block with no
outputs returns `None`. Tuples become SymPy tuples, while lists and dictionaries
remain Python containers. Integer-indexed assignment targets require a SymPy
`IndexedBase` with a shape, supplied through substitution.

Backend discovery skips absent optional libraries, but propagates import errors
inside installed libraries or Symbolite backends.

`vector.vectorize` replaces selected scalar symbols with vector elements. It
always returns `(vector, rewritten)`: omitting `into` creates a fresh anonymous
`Vector()`, while supplying `into` reuses that exact vector. Use `order` for
consecutive positions or `indices` for explicit positions from any mapping.

```python
from symbolite import Real, Vector, substitute, translate, vector
from symbolite.impl import libstd

x, y = Real("x"), Real("y")
expr = x + 10 * y

state, rewritten = vector.vectorize(expr, order=(x, y))
assert translate(substitute(rewritten, {state: (3, 5)}), libstd) == 53

state = Vector("state")
returned, rewritten = vector.vectorize(expr, into=state, indices={x: 3, y: 5})
assert returned is state
assert translate(substitute(rewritten, {state: (1, 2, 0, 3, 0, 5)}), libstd) == 53

inputs = vector.vector_inputs(expr)
assert inputs == (x, y)
state, rewritten = vector.auto_vectorize(expr)
values = {x: 3, y: 5}
packed = tuple(values[symbol] for symbol in inputs)
assert translate(substitute(rewritten, {state: packed}), libstd) == 53
```

Layouts use actual named `Real` or `Symbol` objects, including subclasses, and
leave unlisted symbols unchanged. Supply exactly one of `order` and `indices`.
Repeated symbols in `order` are rejected; shared indices are allowed. Indices
must be nonnegative Python integers, excluding `bool`. Expressions and supported
containers follow `substitute`'s traversal rules, so lists remain lists.

`vector_inputs(expr)` exposes the layout used by `auto_vectorize`: free scalar
symbols without a namespace, sorted by name and deduplicated by structural
equality. Distinct symbol types sharing a name retain their first-occurrence
order. Backend constants such as `real.pi`, existing vectors, and Boolean leaves
are excluded. Namespaced scalar inputs can be selected explicitly with
`vectorize`. Constant expressions have an empty layout and still return a vector.

This replaces the old positional name sequences/mappings, `output_name`, and
`scalar_type` arguments. Migrate `vector.vectorize(expr, ("x", "y"))` to
`state, rewritten = vector.vectorize(expr, order=(x, y))`; use
`into=Vector("state")` to choose a name. `auto_vectorize` now returns the vector
in its first position; use `vector_inputs` to obtain the ordered inputs.

We provide a simple way to call user defined functions.

```python
>>> from symbolite import UserFunction
>>> def abs_times_two(x: float) -> float:
...     return 2 * abs(x)
>>> uf = UserFunction.from_function(abs_times_two)
>>> uf
UserFunction(name='abs_times_two', namespace='user')
>>> translate(uf(-1))
2
```

and you can register implementations for other backends:

```python
>>> def np_abs_times_two(x: float) -> float:
...     return 2 * np.abs(x)
>>> uf.register_impl(np_abs_times_two, libsl=libnumpy)
>>> translate(uf(-1), libnumpy)
2
```

Backend registration does not change a user function's equality or hash, nor
those of expressions containing it. Separately constructed user functions are
distinct, even with the same name and signature. Shallow and deep copies retain
the same function identity and share its implementation registry, so later
registrations remain visible through those copies.

### Symbolic conditions

Symbolic values raise `TypeError` when used with `bool()`, in Python conditions,
or with `not`, `and`, and `or`. Chained comparisons such as `0 < x < 10` also
raise: write `(0 < x) & (x < 10)` to preserve both symbolic conditions. Use `|`
for symbolic disjunction. Compound Boolean support depends on the backend;
the Python code backend and compiled numerical blocks support these operators.

`Boolean(True)` and `Boolean(False)` permit truth conversion because they wrap
direct Python `bool` literals. Named Booleans, nested wrappers, and Boolean
expressions require explicit evaluation. Substitution alone does not evaluate
an expression, and truth conversion never selects a backend or calls a function.

```python
from symbolite import Real, substitute, translate
from symbolite.abstract import Boolean
from symbolite.impl import libstd

assert bool(Boolean(True)) is True
assert bool(Boolean(False)) is False

x = Real("x")
condition = substitute(x < 0, {x: -5})
# bool(condition) raises TypeError; evaluate explicitly instead.
assert bool(translate(condition, libstd)) is True
```

Python `==` and `!=` still compare symbolic objects structurally and return
ordinary booleans. Use `.eq()` and `.ne()` to construct mathematical comparisons.

For both `Real` and `Symbol`, the SymPy backend translates `.eq()` and `.ne()`
to [SymPy `Eq` and `Ne`](https://docs.sympy.org/latest/modules/core.html#sympy.core.relational.Equality).
With SymPy's default evaluation, decidable comparisons reduce to SymPy `true`
or `false`; unresolved comparisons retain their symbols for later `.subs(...)`.
Evaluation follows SymPy's symbol assumptions (including `real=True` for `Real`),
numeric precision, and special-value conventions. For example,
`translate(real.sqrt(1).eq(1.0), libsympy)` returns SymPy `true`, even though its
operands have different numeric representations.

Vector operations have an explicit backend contract:

| Backend | Supported vector inputs and operations | Boolean composition |
|---|---|---|
| Standard library | Indexing and reductions on finite lists/tuples; arithmetic and comparisons through supplied objects' native vector operators | Native Boolean operators on scalars and Boolean masks |
| NumPy | Native array arithmetic, elementwise comparisons, indexing and reductions | Elementwise logical AND, OR and XOR |
| JAX | Native array operations; indexing and reductions also accept finite lists/tuples, with reduction inputs converted to JAX arrays | Elementwise logical AND, OR and XOR |
| SymPy | Symbolic vector indexing; sums and products over explicit finite sequences | Symbolic `And`, `Or` and `Xor` |

For numerical arrays, vector `.eq()` and `.ne()` produce elementwise Boolean
masks. One-dimensional `@` computes a scalar dot product; `sum` and `prod`
produce scalar results, with empty sequences yielding `0` and `1`, respectively.
Broadcasting, numeric precision, dtype promotion, and invalid-input errors follow
the selected backend. Lists and tuples support indexing and reductions in the
standard backend; arithmetic on them raises `TypeError` to avoid concatenation,
repetition, or scalar sequence equality being interpreted as vector mathematics.
Native array indexing follows backend conventions: NumPy raises `IndexError`
for out-of-bounds retrieval, while [JAX clamps retrieval indices](https://docs.jax.dev/en/latest/notebooks/Common_Gotchas_in_JAX.html#out-of-bounds-indexing).

SymPy whole-vector arithmetic and comparisons raise `Unsupported`; a symbolic
`IndexedBase` also needs explicit finite values for reductions. Numerical backends
require named vector and Boolean inputs to be substituted or supplied as block
arguments. SymPy retains these names symbolically.

Generated numerical blocks call the same vector and Boolean primitives as direct
translation, for example `vector.sub(v, 1)` and `boolean.and_(left, right)`.
Indexed access retains native subscript syntax, including assignment targets.
Compilation checks vector and Boolean capabilities before executing generated
source. Every declared primitive is bound to an implementation or `Unsupported`.

### Structural traversal and extensions

`symbolite.ops.traversal` exposes the shared structure used by translation,
substitution, named-value inspection, and tree printing:

- `project(obj)` describes one node as a `Layer(kind, data, children)`.
- `rebuild(layer, children)` reconstructs a node from replacement children.
- `fold(obj, algebra)` interprets nodes bottom-up; the algebra receives a layer
  and the already interpreted children.
- `walk(obj)` yields nodes lazily in preorder.
- `rewrite(obj, replace)` applies replacements before visiting children.
- `transform(obj, rule)` transforms children first, then applies the rule to the
  reconstructed parent.

Rewrite and transform rules return `KEEP` to retain a node. A replacement is
final for that occurrence and is not visited again. Substitution, rewriting,
and transformation produce fresh containers for every traversed exact built-in
list and dictionary, including empty ones. Tuples and symbolic nodes retain
identity when their children do; parents enclosing copied containers are rebuilt.
Shared subtrees are processed per occurrence, so repeated occurrences of an
input list or dictionary produce separate output containers. Numerical user
functions are not memoized. Traversal uses explicit stacks and rejects active
ancestor cycles.

This is container ownership, not a deep copy of every object. Symbolic leaves,
arrays, other foreign leaves, and unadapted container subclasses may remain
shared. Explicit replacements are returned as supplied, and operation-specific
handlers control their own output ownership. With `transform`, a rule returning
`KEEP` retains the rebuilt node, including any fresh containers.

Reconstruction preserves a symbolic wrapper's concrete subclass and extra
state without rerunning its constructor. Rebuilt Blocks and `BlockInfo` records
are checked against the same dependency and output rules as the Block
constructor. With `transform`, automatic Block reconstruction is provisional
until the parent rule finishes, so that rule can repair inputs or outputs to
match its transformed children. The resulting Block or `BlockInfo` is then
validated, including one returned explicitly by the rule. Direct `rebuild`
calls still validate immediately, even inside a transform rule. Custom
rebuilders retain their own validation behavior, and other explicit replacement
subtrees are not visited for validation.

Statement substitution also uses the iterative traversal; Block interfaces
retain their special vector-item mapping policy, and Block names are not
substituted. Native statement translation checks structural cycles and Block
dependencies before calling the backend, without evaluating expressions.
These checks run on every native statement translation because mutable
payloads can change after construction. Registered operation handlers still
prune their subtrees; translation overrides that do not delegate to a native
parent handler remain responsible for their own validation.

```python
from symbolite import Real, substitute

x = Real("x")
original = {"values": [x]}
result = substitute(original, {})
result["values"].append(3)

assert original["values"] == [x]
assert result["values"][0] is x
```

`rewrite` also accepts `replace_layer=callback`. This callback receives the
original node and its projected layer after the initial replacement rule returns
`KEEP`, and can replace it before descent without projecting it a second time.

For example, bottom-up transformation lets a parent see an unwrapped child:

```python
from symbolite.ops.traversal import KEEP, transform

def unwrap_singleton(node):
    if type(node) is list and len(node) == 1:
        return node[0]
    return KEEP

assert transform([[[3]]], unwrap_singleton) == 3
```

`Layer.kind` is an open string tag, independent of backend `Kind`. Built-in
adapters use these payload and child conventions:

| Kind | Data | Children |
|---|---|---|
| `atom` | Original leaf | None |
| `value` | Original symbolic value | Wrapped payload |
| `call` | Original `Call` or `CallInfo` | Function, positional arguments, then keyword values |
| `object` | Original Symbolite wrapper | Metadata fields in order |
| `record` | Metadata record type | Record fields in order |
| `tuple`, `list` | `None` | Elements in order |
| `dict` | `None` | Alternating keys and values in insertion order |

Only `children` are traversed; `data` is reconstruction metadata. Exact built-in
tuple/list/dict objects have adapters. Unadapted container subclasses and foreign
arrays remain atomic. Adapter callbacks should describe structure without
mutating the original object.

For a custom structure, register its projection and its layer subclass's
rebuilder. Choose a distinct kind to keep the built-in payload conventions clear.
Use `translate_layer.register` when the structure needs backend semantics beyond
rebuilding around translated children:

```python
from dataclasses import dataclass
from typing import Any

from symbolite import Real, substitute, translate
from symbolite.impl import libstd
from symbolite.ops import translate_layer
from symbolite.ops.traversal import Layer, project, rebuild

@dataclass(frozen=True)
class Box:
    value: Any

@dataclass(frozen=True)
class BoxLayer(Layer):
    pass

@project.register(Box)
def project_box(obj):
    return BoxLayer("box", None, (obj.value,))

@rebuild.register(BoxLayer)
def rebuild_box(layer, children):
    return Box(children[0])

@translate_layer.register(BoxLayer)
def translate_box(layer, children, libsl):
    return children[0]

x = Real("x")
assert translate(substitute(Box(x + 1), {x: 4}), libstd) == 5
```

Object-level `.register()` handlers take precedence and prune structural
traversal. Existing handlers can delegate to a saved parent and have cycle
protection, but their ordinary Python calls can still reach the recursion limit.
Structural adapters let the traversal process children iteratively;
`translate_layer` handlers then receive those processed children without
recursive parent calls, so they support deeply nested structures.

`tree_view()` also uses structural adapters and iterative traversal. Containers
and custom structures are shown as nested children; expression call formatting
is preserved. A default printer flushes the final line before returning. With a
supplied `Printer`, call `flush_line()` when finished composing output.

### Installing:

```bash
pip install -U symbolite
```

### FAQ

**Q: Is symbolite a replacement for SymPy?**

**A:** No

**Q: Does it aim to be a replacement for SymPy in the future?**

**A:** No
