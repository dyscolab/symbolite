from ...abstract import real as abstract_real
from ...core.function import (
    BinaryFunction,
    BinaryOperator,
    UnaryFunction,
    UnaryOperator,
)

latex_names = {
    abstract_real.eq: "{} = {}",
    abstract_real.ne: "{} \\neq {}",
    abstract_real.lt: "{} < {}",
    abstract_real.le: "{} \\le {}",
    abstract_real.gt: "{} > {}",
    abstract_real.ge: "{} \\ge {}",
    abstract_real.add: "{} + {}",
    abstract_real.sub: "{} - {}",
    abstract_real.mul: "{} \\cdot {}",
    abstract_real.truediv: "\\dfrac{{{}}}{{{}}}",
    abstract_real.mod: "{} \\pmod{}",
    abstract_real.lshift: "{} \\ll {}",
    abstract_real.rshift: "{} \\gg {}",
    abstract_real.and_: "{} \\land {}",
    abstract_real.xor: "{} \\oplus {}",
    abstract_real.or_: "{} \\lor {}",
    abstract_real.neg: "-{}",
    abstract_real.pos: "+{}",
    abstract_real.invert: "~{}",
    abstract_real.abs: "\\left\\lvert {} \\right\\rvert",
    abstract_real.acos: "\\arccos",
    abstract_real.acosh: "\\operatorname{arcosh}",
    abstract_real.asin: "\\arcsin",
    abstract_real.asinh: "\\operatorname{arcsinh}",
    abstract_real.atan: "\\arctan",
    abstract_real.atan2: "\\operatorname{arctan2}",
    abstract_real.atanh: "\\operatorname{arctanh}",
    abstract_real.ceil: "\\left\\lceil {} \\right\\rceil",
    abstract_real.comb: "\\binom{n}{k}",
    abstract_real.copysign: "\\operatorname{copysign}",
    abstract_real.cos: "\\cos",
    abstract_real.cosh: "\\cosh",
    abstract_real.degrees: "\\operatorname{deg}",
    abstract_real.erf: "\\operatorname{erf}",
    abstract_real.erfc: "\\operatorname{erfc}",
    abstract_real.exp: "\\exp",
    abstract_real.expm1: "\\operatorname{expm1}",
    abstract_real.factorial: "{}!",
    abstract_real.floor: "\\left\\lfloor {} \\right\\rfloor",
    abstract_real.fmod: "\\operatorname{fmod}",
    abstract_real.frexp: "\\operatorname{frexp}",
    abstract_real.gamma: "\\Gamma",
    abstract_real.hypot: "\\operatorname{hypot}",
    abstract_real.isfinite: "\\operatorname{isfinite}",
    abstract_real.isinf: "\\operatorname{isinf}",
    abstract_real.isnan: "\\operatorname{isnan}",
    abstract_real.ldexp: "\\operatorname{ldexp}",
    abstract_real.lgamma: "\\ln\\Gamma",
    abstract_real.log: "\\ln",
    abstract_real.log10: "\\log_{10}",
    abstract_real.log1p: "\\operatorname{log1p}",
    abstract_real.log2: "\\log_2",
    abstract_real.modf: "\\operatorname{modf}",
    abstract_real.nextafter: "\\operatorname{nextafter}",
    abstract_real.radians: "\\operatorname{rad}",
    abstract_real.remainder: "\\operatorname{rem}",
    abstract_real.sin: "\\sin",
    abstract_real.sinh: "\\sinh",
    abstract_real.sqrt: "\\sqrt{{{}}}",
    abstract_real.tan: "\\tan",
    abstract_real.tanh: "\\tanh",
    abstract_real.trunc: "\\operatorname{trunc}",
    abstract_real.ulp: "\\operatorname{ulp}",
    abstract_real.le: "{} \\le {}",
    abstract_real.pow: "{}^{{{}}}",
    abstract_real.e: "e",
    abstract_real.inf: "\\infty",
    abstract_real.pi: "\\pi",
    abstract_real.nan: "\\text{NaN}",
    abstract_real.tau: "\\tau",
}


def _get_latex_name(
    obj: UnaryFunction | BinaryFunction | UnaryOperator | BinaryOperator,
) -> str:
    return latex_names[obj]


latex_precedences = {
    abstract_real.abs: 5,
    abstract_real.ceil: 5,
    abstract_real.floor: 5,
    abstract_real.factorial: 4,
    abstract_real.pow: 3,
    abstract_real.sqrt: 3,
}
# Since division is implemented with \dfrac parenthesis are never necessary,
# so it is given the lowest precedence


def _get_latex_precedence(
    obj: UnaryFunction | BinaryFunction | UnaryOperator | BinaryOperator,
) -> int:
    """Some functions are turned into operators for latex conversion
    or given a different precedence."""
    precedence = latex_precedences.get(
        obj, getattr(obj.__symbolite_info__, "precedence", None)
    )
    if precedence is None:
        raise AttributeError(f"{obj} has no precedence")
    else:
        return precedence


never_parentesize = [
    abstract_real.abs,
    abstract_real.floor,
    abstract_real.ceil,
    abstract_real.truediv,
]


def _parenthesize(
    obj: UnaryFunction | BinaryFunction | UnaryOperator | BinaryOperator,
) -> bool:
    return obj not in never_parentesize
