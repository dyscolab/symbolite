"""Native composition of Boolean scalars and Boolean array masks."""

import operator

from ...core import Unsupported

and_ = operator.and_
or_ = operator.or_
xor = operator.xor

Boolean = Unsupported
