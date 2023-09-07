import abc

from .models import *


class LokiClientBase(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def push(self, data: list[Stream]):
        """"""


class LokiPushBase(metaclass=abc.ABCMeta):

    def __init__(self):
        self._labels = {}

    def set_label(self, k: str, v: str) -> None:
        self._labels[k] = v

    def set_labels(self, labels: dict) -> None:
        self._labels.update(labels)
