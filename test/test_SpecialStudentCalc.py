# -*- coding: utf-8 -*-
import pytest

from src.SpecialStudentCalc import SpecialStudentCalc
from src.Types import DataType


class TestSpecialStudentCalc:

    @pytest.fixture()
    def data(self) -> DataType:
        return {
            "Иванов Иван Иванович": [
                ("математика", 80),
                ("литература", 90),
                ("программирование", 76)
            ],
            "Петров Петр Петрович": [
                ("математика", 100),
                ("химия", 90),
                ("физика", 61)
            ]
        }

    def test_init(self, data: DataType) -> None:
        calc = SpecialStudentCalc(data)
        assert calc.data == data
        assert calc.min_score == 76
        assert calc.min_subjects == 3

    def test_find_student_with_three_good_scores(self,
                                                 data: DataType) -> None:
        assert SpecialStudentCalc(data).find() == "Иванов Иван Иванович"

    def test_boundary_score_is_seventy_six(self, data: DataType) -> None:
        assert SpecialStudentCalc(data).find() is not None

    def test_no_suitable_student(self) -> None:
        data: DataType = {
            "Петров Петр Петрович": [
                ("математика", 100),
                ("химия", 90),
                ("физика", 61)
            ]
        }
        assert SpecialStudentCalc(data).find() is None

    def test_only_two_good_scores_is_not_enough(self) -> None:
        data: DataType = {
            "Сидоров Сидор Сидорович": [
                ("математика", 90),
                ("физика", 95),
                ("химия", 75)
            ]
        }
        assert SpecialStudentCalc(data).find() is None

    def test_find_or_message_when_found(self, data: DataType) -> None:
        message = SpecialStudentCalc(data).find_or_message()
        assert message == "Найден студент: Иванов Иван Иванович"

    def test_find_or_message_when_absent(self) -> None:
        calc = SpecialStudentCalc({})
        message = calc.find_or_message()
        assert "нет" in message
