import threading


class PseudoFuture(threading.Event):
    """A future-like interface for synchronous code."""

    def __init__(self):
        """Initialize the PseudoFuture."""
        super().__init__()

    def set_result(self, result):
        """Set the result for the future."""
        self._result = result
        self.set()

    def set_exception(self, exception):
        """Set the exception for the future."""
        self._exception = exception
        self.set()

    def result(self):
        """Return the result of the future, or raise the exception."""
        self.wait()
        if hasattr(self, "_exception"):
            raise self._exception
        return self._result
