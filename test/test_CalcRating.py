# -*- coding: utf-8 -*-
from src.Types import DataType
from src.CalcRating import CalcRating
import pytest

RatingsType = dict[str, float]


class TestCalcRating:

    @pytest.fixture()
    def input_data(self) -> tuple[DataType, RatingsType]:
        data: DataType = {
            "Дубов Андрей Сергеевич":
                [
                    ("математика", 80),
                    ("русск яз", 76),
                    ("программирование", 100)
                ],

            "Барсуков Олег Николаевич":
                [
                    ("математика", 61),
                    ("русск яз", 80),
                    ("программирование", 78),
                    ("философия", 97)
                ]
        }

        rating_scores: RatingsType = {
            "Дубов Андрей Сергеевич": 85.3333,
            "Барсуков Олег Николаевич": 79.0000
        }
        return data, rating_scores

    def test_init_calc_rating(self, input_data: tuple[DataType,
                                                      RatingsType]) -> None:
        calc_rating = CalcRating(input_data[0])
        assert input_data[0] == calc_rating.data

    def test_calc(self, input_data: tuple[DataType,
                                          RatingsType]) -> None:

        rating = CalcRating(input_data[0]).calc()
        for student in rating.keys():
            rating_score = rating[student]
            assert pytest.approx(rating_score,
                                 abs=0.001) == input_data[1][student]
