from threading import Event


class PseudoFuture(Event):
    def __init__(self):
        super().__init__()

    def set_result(self, result):
        self._result = result
        self.set()

    def set_exception(self, exception):
        self._exception = exception
        self.set()

    def result(self):
        self.wait()
        if hasattr(self, "_exception"):
            raise self._exception
        return self._result
