"""Operation overrides shared by expression traversal consumers."""

from collections.abc import Callable, Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Any, Protocol

from ..core.symbolite_object import SymboliteObject, get_symbolite_info
from ._traversal import KEEP, walk

type _Override = tuple[Callable[..., Any], Any]


@dataclass
class _OverrideScope:
    identity: int
    active: bool = True


class _SingleDispatch(Protocol):
    def dispatch(self, cls: type[Any]) -> Callable[..., Any]: ...


class TraversalDispatch:
    """Select operation overrides before structural descent.

    Each traversal skips wrapper dispatch at its root: entry dispatch has
    already run, and saved parent handlers must be able to delegate here.
    Optional metadata dispatch preserves each operation's historical rules.
    Handler identity is compared without hashing callable extensions.
    Overrides are guarded across parent delegation, including generator steps.
    Legacy callbacks can recurse; structural adapters and layer algebras keep
    nested processing in the iterative traversal instead.
    """

    def __init__(
        self,
        operation: _SingleDispatch,
        *,
        metadata_exclusions: tuple[type[Any], ...] | None = None,
        terminal_handlers: tuple[Callable[..., Any], ...] = (),
    ) -> None:
        self.operation = operation
        self.default = operation.dispatch(object)
        self.metadata_exclusions = metadata_exclusions
        # Retain the callbacks so their identities cannot be reused after a
        # registration changes. Arbitrary extension callables need not hash.
        self._terminal_handlers = terminal_handlers
        self._terminal_handler_ids = frozenset(map(id, terminal_handlers))
        self._active_overrides: ContextVar[tuple[_OverrideScope, ...]] = ContextVar(
            "symbolite_active_overrides", default=()
        )

    @contextmanager
    def _guard(self, node: Any) -> Iterator[None]:
        active = tuple(scope for scope in self._active_overrides.get() if scope.active)
        identity = id(node)
        if any(scope.identity == identity for scope in active):
            raise ValueError(f"Cycle detected while delegating {type(node).__name__}.")
        scope = _OverrideScope(identity)
        token = self._active_overrides.set((*active, scope))
        try:
            yield
        finally:
            # A copied context (for example, a newly created asyncio task)
            # must not retain an expired override after its parent returns.
            scope.active = False
            self._active_overrides.reset(token)

    def invoke(self, node: Any, selected: _Override, *args: Any) -> Any:
        """Run an override with cycle protection across parent delegation."""
        handler, target = selected
        if id(handler) in self._terminal_handler_ids:
            return handler(target, *args)
        with self._guard(node):
            return handler(target, *args)

    def iterate(self, node: Any, selected: _Override) -> Iterator[Any]:
        """Guard generator execution without leaking context across yields."""
        handler, target = selected
        with self._guard(node):
            iterator = iter(handler(target))
        finished = object()
        try:
            while True:
                with self._guard(node):
                    result = next(iterator, finished)
                if result is finished:
                    return
                yield result
        finally:
            close = getattr(iterator, "close", None)
            if close is not None:
                close()

    def select(self, node: Any, *, root: bool = False) -> _Override | None:
        if not root:
            handler = self.operation.dispatch(type(node))
            if handler is not self.default:
                return handler, node
        if (
            self.metadata_exclusions is not None
            and isinstance(node, SymboliteObject)
            and not isinstance(node, self.metadata_exclusions)
        ):
            info = get_symbolite_info(node)
            handler = self.operation.dispatch(type(info))
            if handler is not self.default:
                return handler, info
        return None

    def visit(
        self,
        *args: Any,
        fallback: Callable[[Any], Any] | None = None,
    ) -> Callable[[Any], Any]:
        """Create a fresh previsit for a fold/rewrite, with optional policy."""
        root = True

        def apply(node: Any) -> Any:
            nonlocal root
            selected = self.select(node, root=root)
            root = False
            if selected is not None:
                return self.invoke(node, selected, *args)
            return KEEP if fallback is None else fallback(node)

        return apply

    def walk(self, obj: Any) -> Iterator[tuple[Any, _Override | None]]:
        """Yield nodes with their overrides, pruning overridden subtrees."""
        selected: _Override | None = None

        def descend(_node: Any) -> bool:
            # walk yields a node before consulting descend. Reuse its selection
            # when it resumes, without dispatching the same occurrence twice.
            return selected is None

        for index, node in enumerate(walk(obj, descend=descend)):
            selected = self.select(node, root=index == 0)
            yield node, selected
