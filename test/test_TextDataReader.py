# -*- coding: utf-8 -*-
import pytest

from src.Types import DataType
from src.TextDataReader import TextDataReader


class TestTextDataReader:

    @pytest.fixture()
    def file_and_data_content(self) -> tuple[str, DataType]:
        text = "Имя Отчество Фамилия\n" + \
               "    предмет1:91\n" + "    предмет2:100\n" + \
               "Имя Отчество Фамилия2\n" + \
               "    предмет1:87\n" + "    предмет2:78\n"

        data = {
            "Имя Отчество Фамилия": [
                ("предмет1", 91), ("предмет2", 100)
            ],
            "Имя Отчество Фамилия2": [
                ("предмет1", 87), ("предмет2", 78)
            ]
        }
        return text, data

    @pytest.fixture()
    def filepath_and_data(self,
                          file_and_data_content: tuple[str, DataType],
                          tmpdir) -> tuple[str, DataType]:
        p = tmpdir.mkdir("datadir").join("my_data.txt")
        p.write_text(file_and_data_content[0], encoding='utf-8')
        return str(p), file_and_data_content[1]

    def test_read(self, filepath_and_data: tuple[str, DataType]) -> None:
        file_content = TextDataReader().read(filepath_and_data[0])
        assert file_content == filepath_and_data[1]
