import asyncio

import pandas as pd
import pytest
from fastapi import HTTPException

from data.dtos.mailing.mailing_request import (
    MultipleFilesRequest,
    SingleFileRequest,
    TwoFilesRequest,
)
from services.mailing.mailing_service import MailingService


def run(coroutine):
    return asyncio.run(coroutine)


def single_request(csv_upload, content, filename="input.csv"):
    return SingleFileRequest(file=csv_upload(content, filename))


def two_files_request(csv_upload, first_content, second_content):
    return TwoFilesRequest(
        first_file=csv_upload(first_content, "first.csv"),
        second_file=csv_upload(second_content, "second.csv"),
    )


def test_read_csv_preserves_text_and_supports_cp1252():
    content = "Nome;CEP\nJoão;00123"

    dataframe = MailingService._read_csv(content.encode("cp1252"))

    assert dataframe.iloc[0].to_dict() == {"Nome": "João", "CEP": "00123"}
    assert all(pd.api.types.is_string_dtype(dtype) for dtype in dataframe.dtypes)


def test_read_csv_supports_utf8_bom(csv_upload):
    upload = csv_upload("Nome;CEP\nAção;01000", encoding="utf-8-sig")

    dataframe = MailingService._read_csv(asyncio.run(upload.read()))

    assert dataframe.columns.tolist() == ["Nome", "CEP"]
    assert dataframe.iloc[0]["Nome"] == "Ação"


def test_hygiene_service_generates_incremented_filename(csv_upload):
    request = two_files_request(
        csv_upload,
        "DDDNUM;Nome\n111;A\n222;B",
        "number\nBR111",
    )

    result = run(MailingService().hygiene_mailing(request))

    assert result.arquivo_gerado == "first_1.csv"
    assert result.conteudo.decode("cp1252").splitlines() == ["DDDNUM;Nome", "222;B"]


def test_hygiene_service_increments_existing_suffix(csv_upload):
    request = TwoFilesRequest(
        first_file=csv_upload("DDDNUM\n222", "mailing_4.csv"),
        second_file=csv_upload("number\nBR111", "filter.csv"),
    )

    result = run(MailingService().hygiene_mailing(request))

    assert result.arquivo_gerado == "mailing_5.csv"


def test_clean_service_returns_clean_csv(csv_upload):
    content = (
        "CNPJ;CEP;Telefone 1;Número;Tipo;Endereço;Opção pelo MEI\n"
        "12.345;01.000-000;BR11999999999;10;Rua;Centro;S\n"
    )
    result = run(MailingService().clean_mailing(single_request(csv_upload, content)))

    output = result.conteudo.decode("cp1252")
    assert result.arquivo_gerado == "input_clean.csv"
    assert "12345.;01000000;11999999999" in output


def test_pre_prospecting_service_returns_expected_columns(csv_upload):
    content = "CNPJ;CEP;Número;Telefone 1\n001.234;01000.;10;11999999999\n"
    result = run(MailingService().pre_prospecting(single_request(csv_upload, content)))

    assert result.arquivo_gerado == "input_pre_prospecting.csv"
    assert result.conteudo.decode("cp1252").splitlines() == [
        "Documento;CEP;NUMERO;TELEFONE",
        "001234;01000.;10;11999999999",
    ]


def test_match_service_marks_coverage(csv_upload):
    request = two_files_request(
        csv_upload,
        "CEP_Número;Nome\n01000;A\n02000;B",
        "referencia\n01000",
    )

    result = run(MailingService().mark_mailing_matches(request))

    assert "01000;A;SIM" in result.conteudo.decode("cp1252")
    assert "02000;B;NÃO" in result.conteudo.decode("cp1252")


def test_concatenate_service_combines_files(csv_upload):
    request = MultipleFilesRequest(
        files=[
            csv_upload("value\na\n", "first.csv"),
            csv_upload("value\nb\n", "second.csv"),
        ]
    )

    result = run(MailingService().concatenate_mailing(request))

    assert result.arquivo_gerado == "first_concatenated.csv"
    assert result.conteudo.decode("utf-8-sig").splitlines() == ["value", "a", "b"]


@pytest.mark.parametrize(
    ("method_name", "content", "missing"),
    [
        ("pre_prospecting", "CNPJ;CEP\n1;01000", "Telefone 1"),
        ("clean_mailing", "CNPJ;CEP\n1;01000", "Telefone 1"),
    ],
)
def test_single_file_service_reports_missing_columns(
    csv_upload,
    method_name,
    content,
    missing,
):
    request = single_request(csv_upload, content)

    with pytest.raises(HTTPException) as error:
        run(getattr(MailingService(), method_name)(request))

    assert error.value.status_code == 400
    assert missing in error.value.detail
    assert "input.csv" in error.value.detail


def test_hygiene_service_reports_missing_columns(csv_upload):
    request = two_files_request(csv_upload, "DDDNUM\n111", "other\nBR111")

    with pytest.raises(HTTPException) as error:
        run(MailingService().hygiene_mailing(request))

    assert error.value.status_code == 400
    assert "number" in error.value.detail
    assert "second.csv" in error.value.detail


def test_match_service_rejects_reference_without_columns(csv_upload):
    request = two_files_request(csv_upload, "CEP_Número\n01000", "")

    with pytest.raises(HTTPException) as error:
        run(MailingService().mark_mailing_matches(request))

    assert error.value.status_code == 400
    assert "second.csv" in error.value.detail


def test_service_rejects_empty_csv(csv_upload):
    request = single_request(csv_upload, "", "empty.csv")

    with pytest.raises(HTTPException) as error:
        run(MailingService().pre_prospecting(request))

    assert error.value.status_code == 400
    assert "empty.csv" in error.value.detail
