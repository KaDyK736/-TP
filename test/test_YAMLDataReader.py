# -*- coding: utf-8 -*-
import pytest

from src.Types import DataType
from src.YAMLDataReader import YAMLDataReader


class TestYAMLDataReader:

    @pytest.fixture()
    def file_and_data_content(self) -> tuple[str, DataType]:
        text = "Иванов Иван Иванович:\n" + \
               "    математика: 80\n" + \
               "    литература: 100\n" + \
               "Петров Петр Петрович:\n" + \
               "    физика: 76\n" + \
               "    химия: 61\n"

        data = {
            "Иванов Иван Иванович": [
                ("математика", 80), ("литература", 100)
            ],
            "Петров Петр Петрович": [
                ("физика", 76), ("химия", 61)
            ]
        }
        return text, data

    @pytest.fixture()
    def filepath_and_data(self,
                          file_and_data_content: tuple[str, DataType],
                          tmpdir) -> tuple[str, DataType]:
        p = tmpdir.mkdir("datadir").join("my_data.yaml")
        p.write_text(file_and_data_content[0], encoding='utf-8')
        return str(p), file_and_data_content[1]

    def test_read(self, filepath_and_data: tuple[str, DataType]) -> None:
        file_content = YAMLDataReader().read(filepath_and_data[0])
        assert file_content == filepath_and_data[1]

    def test_read_empty_file(self, tmpdir) -> None:
        p = tmpdir.mkdir("datadir").join("empty.yaml")
        p.write_text("", encoding='utf-8')
        assert YAMLDataReader().read(str(p)) == {}

    def test_read_student_without_subjects(self, tmpdir) -> None:
        p = tmpdir.mkdir("datadir").join("no_subjects.yaml")
        p.write_text("Иванов Иван Иванович:\n", encoding='utf-8')
        assert YAMLDataReader().read(str(p)) == \
            {"Иванов Иван Иванович": []}

    def test_read_string_scores(self, tmpdir) -> None:
        p = tmpdir.mkdir("datadir").join("str_scores.yaml")
        p.write_text("Иванов Иван Иванович:\n    математика: '80'\n",
                     encoding='utf-8')
        assert YAMLDataReader().read(str(p)) == \
            {"Иванов Иван Иванович": [("математика", 80)]}
