# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod

from Types import DataType


class DataReader(ABC):

    @abstractmethod
    def read(self, path: str) -> DataType:
        pass
