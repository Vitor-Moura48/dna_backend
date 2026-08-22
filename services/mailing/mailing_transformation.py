import numpy as np
import pandas as pd


def hygiene_mailing_transformation(
	base_dataframe: pd.DataFrame,
	filter_dataframe: pd.DataFrame,
) -> pd.DataFrame:
	base_dataframe = base_dataframe.copy()
	filter_dataframe = filter_dataframe.copy()

	base_dataframe["DDDNUM"] = base_dataframe["DDDNUM"].astype(str)
	filter_dataframe["number"] = filter_dataframe["number"].astype(str)
	filter_dataframe["number"] = filter_dataframe["number"].str[2:]

	return base_dataframe[
		~base_dataframe["DDDNUM"].isin(filter_dataframe["number"])
	]


def clean_mailing_transformation(dataframe: pd.DataFrame) -> pd.DataFrame:
	dataframe = dataframe.copy()

	dataframe["CNPJ"] = dataframe["CNPJ"].str.replace(r"\D", "", regex=True)
	dataframe["CEP"] = dataframe["CEP"].str.replace(r"\D", "", regex=True)
	dataframe["CNPJ"] += "."

	dataframe["Telefone 1"] = dataframe["Telefone 1"].astype(str)
	dataframe["Telefone 1"] = dataframe["Telefone 1"].str[2:]
	dataframe = dataframe[dataframe["Telefone 1"].str.len() == 11]
	dataframe = dataframe.drop_duplicates(subset="Telefone 1")

	dataframe["CEP_Número"] = dataframe["CEP"] + dataframe["Número"]
	dataframe["Tipo_Endereço"] = dataframe["Tipo"] + " " + dataframe["Endereço"]
	dataframe["CEP_Número"] = dataframe["CEP_Número"].str.replace(
		r"[/\.\- ]", "", regex=True
	)
	dataframe["Opção pelo MEI"] = np.where(
		dataframe["Opção pelo MEI"] == "S", "MEI", "CNPJ"
	)

	return dataframe


def pre_prospecting_transformation(dataframe: pd.DataFrame) -> pd.DataFrame:
	dataframe = dataframe.copy()
	dataframe["CNPJ"] = dataframe["CNPJ"].str.replace(".", "", regex=False)

	result_dataframe = dataframe[["CNPJ", "CEP", "Telefone 1"]].copy()
	return result_dataframe.rename(
		columns={"CNPJ": "Documento", "Telefone 1": "Telefone"}
	)


def mark_mailing_matches_transformation(
	base_dataframe: pd.DataFrame,
	reference_dataframe: pd.DataFrame,
) -> pd.DataFrame:
	base_dataframe = base_dataframe.copy()
	base_dataframe["Cobertura"] = np.where(
		base_dataframe["CEP_Número"].isin(reference_dataframe.iloc[:, 0]),
		"SIM",
		"NÃO",
	)
	return base_dataframe


def concatenate_mailing_transformation(
	dataframes: list[pd.DataFrame],
) -> pd.DataFrame:
	return pd.concat(dataframes, ignore_index=True)
