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

And by the way, checkout `vectorize` and `auto_vectorize` functions
in the vector module.

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
>>> uf.register_impl(libnumpy, np_abs_times_two)
>>> translate(uf(-1), libnumpy)
2
```

### Installing:

```bash
pip install -U symbolite
```

### FAQ

**Q: Is symbolite a replacement for SymPy?**

**A:** No

**Q: Does it aim to be a replacement for SymPy in the future?**

**A:** No
