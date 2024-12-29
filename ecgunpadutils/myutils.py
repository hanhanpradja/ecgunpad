from threading import Thread
import traceback

class ExceptionThread(Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.exception = None
        self.tracebackexcept = None
    
    def run(self):
        try:
            if self._target:
                self._target(*self._args, **self._kwargs)
        except Exception as e:
            self.exception = e
            self.tracebackexcept = traceback.format_exc()