# -*- coding: utf-8 -*-
from DataReader import DataReader
from Types import DataType


class TextDataReader(DataReader):

    def __init__(self) -> None:
        self.key: str = ""
        self.students: DataType = {}

    def read(self, path: str) -> DataType:
        with open(path, encoding='utf-8') as file:
            for line in file:
                if not line.startswith(" "):
                    self.key = line.strip()
                    self.students[self.key] = []
                else:
                    subj, score = line.split(":", maxsplit=1)
                    self.students[self.key].append(
                        (subj.strip(), int(score.strip())))
        return self.students
