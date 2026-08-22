import io

import pytest
from fastapi import UploadFile


@pytest.fixture
def csv_upload():
    def create_upload(content: str, filename: str = "input.csv", encoding: str = "cp1252"):
        return UploadFile(
            filename=filename,
            file=io.BytesIO(content.encode(encoding)),
        )

    return create_upload

# .\.venv\Scripts\python.exe -m pytest tests -v