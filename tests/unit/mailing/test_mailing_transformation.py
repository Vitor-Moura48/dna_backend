import pandas as pd

from services.mailing.mailing_transformation import (
    clean_mailing_transformation,
    concatenate_mailing_transformation,
    hygiene_mailing_transformation,
    mark_mailing_matches_transformation,
    pre_prospecting_transformation,
)


def test_hygiene_removes_numbers_in_filter():
    base = pd.DataFrame({"DDDNUM": ["111", "222"]})
    filter_dataframe = pd.DataFrame({"number": ["BR111"]})

    result = hygiene_mailing_transformation(base, filter_dataframe)

    assert result["DDDNUM"].tolist() == ["222"]
    assert base["DDDNUM"].tolist() == ["111", "222"]


def test_hygiene_keeps_unmatched_numbers():
    result = hygiene_mailing_transformation(
        pd.DataFrame({"DDDNUM": ["111"]}),
        pd.DataFrame({"number": ["BR999"]}),
    )

    assert result["DDDNUM"].tolist() == ["111"]


def test_clean_normalizes_values_filters_phones_and_removes_duplicates():
    dataframe = pd.DataFrame(
        {
            "CNPJ": ["12.345", "98/765", "98/765"],
            "CEP": ["01.000-000", "02.000", "02.000"],
            "Telefone 1": ["BR11999999999", "BR11888888888", "BR11888888888"],
            "Número": ["10", "20", "20"],
            "Tipo": ["Rua", "Av", "Av"],
            "Endereço": ["Centro", "Norte", "Norte"],
            "Opção pelo MEI": ["S", "N", "N"],
        }
    )

    result = clean_mailing_transformation(dataframe)

    assert result["CNPJ"].tolist() == ["12345.", "98765."]
    assert result["CEP_Número"].tolist() == ["0100000010", "0200020"]
    assert result["Telefone 1"].tolist() == ["11999999999", "11888888888"]
    assert result["Opção pelo MEI"].tolist() == ["MEI", "CNPJ"]
    assert len(result) == 2


def test_clean_discards_phones_without_eleven_digits():
    dataframe = pd.DataFrame(
        {
            "CNPJ": ["123"],
            "CEP": ["01000"],
            "Telefone 1": ["BR123"],
            "Número": ["1"],
            "Tipo": ["Rua"],
            "Endereço": ["Centro"],
            "Opção pelo MEI": ["S"],
        }
    )

    assert clean_mailing_transformation(dataframe).empty


def test_pre_prospecting_selects_and_renames_columns():
    dataframe = pd.DataFrame(
        {
            "CNPJ": ["12.345"],
            "CEP": ["01000."],
            "Número": ["1456D2"],
            "Telefone 1": ["11999999999"],
            "extra": ["ignored"],
        }
    )

    result = pre_prospecting_transformation(dataframe)

    assert result.to_dict("records") == [
        {"Documento": "12345", "CEP": "01000.", "NUMERO": "1456D2", "TELEFONE": "11999999999"}
    ]


def test_mark_matches_marks_sim_and_nao():
    base = pd.DataFrame({"CEP_Número": ["01000", "02000"]})
    reference = pd.DataFrame({"cep": ["01000"]})

    result = mark_mailing_matches_transformation(base, reference)

    assert result["Cobertura"].tolist() == ["SIM", "NÃO"]
    assert "Cobertura" not in base


def test_concatenate_combines_dataframes_and_preserves_order():
    first = pd.DataFrame({"value": ["a"]})
    second = pd.DataFrame({"value": ["b", "c"]})

    result = concatenate_mailing_transformation([first, second])

    assert result.decode("utf-8-sig").splitlines() == ["value", "a", "b", "c"]


def test_concatenate_aligns_different_columns_with_empty_values():
    first = pd.DataFrame({"A": ["1"], "B": ["2"]})
    second = pd.DataFrame({"B": ["3"], "C": ["4"]})

    result = concatenate_mailing_transformation([first, second])

    assert result.decode("utf-8-sig").splitlines() == [
        "A;B;C",
        "1;2;",
        ";3;4",
    ]
