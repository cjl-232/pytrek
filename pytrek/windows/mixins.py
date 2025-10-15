import abc

from ..states import State


class KeyHandlerMixin:
    @abc.abstractmethod
    def handle_key(self, key: int) -> State:
        """Handle key presses when this instance is focused."""
