![Package](https://img.shields.io/pypi/v/symbolite?label=symbolite)
![CodeStyle](https://img.shields.io/badge/code%20style-black-000000.svg)
![License](https://img.shields.io/pypi/l/symbolite?label=license)
![PyVersion](https://img.shields.io/pypi/pyversions/symbolite?label=python)
[![CI](https://github.com/dyscolab/symbolite/actions/workflows/ci.yml/badge.svg)](https://github.com/dyscolab/symbolite/actions/workflows/ci.yml)
[![Lint](https://github.com/dyscolab/symbolite/actions/workflows/lint.yml/badge.svg)](https://github.com/dyscolab/symbolite/actions/workflows/lint.yml)

# symbolite: a minimal symbolic Python package

Symbolite lets you build mathematical expressions with ordinary Python operators.
Keep expressions symbolic, substitute values, and translate them into numerical
results, SymPy expressions, or code using a selected backend.

## Installation

Requires Python 3.12 or later.

```bash
pip install -U symbolite
```

## Quick start

Use `Symbol` for generic symbolic values, `Real` for real scalars, and `Vector`
for vectors.

```python
from symbolite import Real, substitute, translate
from symbolite.impl import libstd
from symbolite.ops import as_code

x, y = Real("x"), Real("y")
expr = x + 3 * y
print(as_code(expr))  # x + 3 * y

filled = substitute(expr, {x: 5, y: 2})
print(as_code(filled))  # 5 + 3 * 2
print(translate(filled, libstd))  # 11
```

Substitution builds another symbolic expression. Translation uses the backend
passed as `libsl` to evaluate or represent it. Numerical backends require values
for named inputs; SymPy can keep them symbolic. Use `as_code` to display an
expression as Python code.

Mathematical functions are available in `real` and `vector`:

```python
from symbolite import Vector, real, vector

print(translate(real.cos(0), libstd))  # 1.0

v = Vector("v")
total = vector.sum(v)
print(translate(substitute(total, {v: (1, 2, 3)}), libstd))  # 6.0
```

## Backends

Implementations live in `symbolite.impl`. Install optional libraries separately
when using their backends.

| Backend | Purpose |
| --- | --- |
| `libstd` | Numerical evaluation with the Python standard library |
| `libnumpy` | NumPy array operations |
| `libjax` | JAX array operations |
| `libsympy` | SymPy symbolic expressions |
| `libpythoncode` | Python source generation |
| `liblatex` | LaTeX expression formatting |

```python
from symbolite.impl import libsympy

print(translate(expr, libsympy))  # x + 3*y
```

Supported operations and numerical behavior depend on the backend. For example,
standard-library lists and tuples support vector indexing and reductions;
NumPy and JAX arrays also support vector arithmetic and elementwise comparisons.

## Packing scalar inputs into a vector

`vector.vectorize` replaces selected scalar symbols with vector elements and
returns `(vector, rewritten_expression)`:

```python
state, rewritten = vector.vectorize(expr, order=(x, y))
print(translate(substitute(rewritten, {state: (5, 2)}), libstd))  # 11
```

Use `into=Vector("state")` to supply a named vector, or `indices={x: 3, y: 5}`
instead of `order` to choose explicit positions. `vector.auto_vectorize(expr)`
selects free scalar inputs automatically; `vector.vector_inputs(expr)` gives
their order.

## User functions

Wrap a Python callable to use it in symbolic expressions:

```python
from symbolite import UserFunction


def abs_times_two(value):
    return 2 * abs(value)


uf = UserFunction.from_function(abs_times_two)
print(translate(uf(-1), libstd))  # 2
```

Register a backend-specific implementation with
`uf.register_impl(function, libsl=backend)`.

## Symbolic conditions

Use `&` and `|` to combine symbolic conditions, such as `(0 < x) & (x < 10)`.
Evaluate conditions explicitly with `translate` before using them in Python
control flow. Symbolic expressions cannot be used directly with `bool()`, `not`,
`and`, `or`, or chained comparisons.

Python `==` and `!=` compare symbolic objects structurally. Use `.eq()` and
`.ne()` to build mathematical equality and inequality expressions.

## Building larger workflows

- `Assign` and `Block` in `symbolite.abstract` describe computations with inputs
  and outputs. Numerical backends translate blocks into callable functions;
  `libpythoncode` generates their source.
- `symbolite.ops.traversal` provides walking, rewriting, transformation, and
  structural adapters for custom types.
- `symbolite.ops.tree_view` displays the structure of an expression.
