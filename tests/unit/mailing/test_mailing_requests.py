import io

import pytest
from fastapi import UploadFile

from data.dtos.mailing.mailing_request import (
    MultipleFilesRequest,
    SingleFileRequest,
    TwoFilesRequest,
)


def upload(filename):
    return UploadFile(filename=filename, file=io.BytesIO())


def test_single_file_request_requires_filename():
    request = SingleFileRequest(file=upload(None))

    with pytest.raises(ValueError, match="nome válido"):
        request.validate_input()


def test_two_files_request_requires_both_filenames():
    request = TwoFilesRequest(first_file=upload("first.csv"), second_file=upload(None))

    with pytest.raises(ValueError, match="nomes válidos"):
        request.validate_input()


@pytest.mark.parametrize("files", [[], [upload("only.csv")]])
def test_multiple_files_request_requires_at_least_two_files(files):
    request = MultipleFilesRequest(files=files)

    with pytest.raises(ValueError, match="pelo menos dois"):
        request.validate_input()


def test_multiple_files_request_rejects_file_without_filename():
    request = MultipleFilesRequest(files=[upload("first.csv"), upload(None)])

    with pytest.raises(ValueError, match="nome válido"):
        request.validate_input()
