# -*- coding: utf-8 -*-
from typing import Optional

from Types import DataType


class SpecialStudentCalc:
    """Индивидуальное задание, вариант 6.

    Ищет студента, имеющего не менее ``min_score`` баллов минимум
    по ``min_subjects`` дисциплинам. Если таких студентов
    несколько, возвращается любой из них.
    """

    def __init__(self, data: DataType, min_score: int = 76,
                 min_subjects: int = 3) -> None:
        self.data: DataType = data
        self.min_score: int = min_score
        self.min_subjects: int = min_subjects

    def find(self) -> Optional[str]:
        for student in self.data:
            good = [subject for subject in self.data[student]
                    if subject[1] >= self.min_score]
            if len(good) >= self.min_subjects:
                return student
        return None

    def find_or_message(self) -> str:
        student = self.find()
        if student is None:
            return ("Студентов с {} и более баллами минимум по {} "
                    "дисциплинам нет".format(self.min_score,
                                             self.min_subjects))
        return "Найден студент: {}".format(student)
