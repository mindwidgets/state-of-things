try:
    from typing import List
except ImportError:
    pass


class Observers:
    def __init__(self) -> None:
        self._observers: List = []

    def attach(self, observer: object):
        self._observers.append(observer)

    def detach(self, observer: object):
        self._observers.remove(observer)

    def notify(self, event_name: str, *params: tuple):
        for observer in self._observers:
            handler = getattr(observer, event_name, None)
            if callable(handler):
                handler(*params)
