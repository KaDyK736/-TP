# -*- coding: utf-8 -*-
import yaml

from DataReader import DataReader
from Types import DataType


class YAMLDataReader(DataReader):

    def __init__(self) -> None:
        self.students: DataType = {}

    def read(self, path: str) -> DataType:
        with open(path, encoding='utf-8') as file:
            raw = yaml.safe_load(file)
        self.students = {}
        if not raw:
            return self.students
        for student, subjects in raw.items():
            self.students[str(student)] = [
                (str(subject), int(score))
                for subject, score in (subjects or {}).items()
            ]
        return self.students
