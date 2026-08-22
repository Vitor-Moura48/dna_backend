import pandas as pd
import io, numpy as np
from os.path import splitext
from typing import List
from data.dtos.mailing.mailing_request import (
    HygieneMailingRequest,
    CleanMailingRequest,
    MatchMailingRequest,
    ConcatenateMailingRequest,
)
from data.dtos.mailing.mailing_response import HygieneMailingResponse

class MailingService:
    def __init__(self):
        pass

    @staticmethod
    def _read_csv(contents: bytes) -> pd.DataFrame:
        for encoding in ("utf-8-sig", "cp1252", "latin1", "utf-16"):
            try:
                return pd.read_csv(io.BytesIO(contents), sep=";", encoding=encoding)
            except UnicodeError:
                continue

        # Mantem a importacao funcionando quando houver bytes isolados corrompidos.
        return pd.read_csv(
            io.BytesIO(contents),
            sep=";",
            encoding="cp1252",
            encoding_errors="replace",
        )

    async def hygiene_mailing(self, request: HygieneMailingRequest) -> HygieneMailingResponse:

        base_contents = await request.base_file.read()
        base_df = self._read_csv(base_contents)

        filter_contents = await request.filter_file.read()
        filter_df = self._read_csv(filter_contents)


        # Converte as colunas de número para string
        base_df["DDDNUM"] = base_df["DDDNUM"].astype(str)
        filter_df["number"] = filter_df["number"].astype(str)

        # Remove o prefixo "BR" da coluna filter_df
        filter_df["number"] = filter_df["number"].str[2:]

        # Filtra os registros do base_df que não estão presentes no filter_df
        filtered_df = base_df[~base_df["DDDNUM"].isin(filter_df["number"])]


        # Retorna o DataFrame filtrado como um novo arquivo CSV
        base_file_name = splitext(request.base_file.filename)[0]
        parts = base_file_name.rsplit("_", 1)

        if len(parts) == 2 and parts[1].isdigit():
            prefix = parts[0]
            num = int(parts[1])
        else:
            prefix = base_file_name
            num = 0

        new_file_name = f"{prefix}_{num + 1}.csv" # Incrementa o número do arquivo


        csv_content = filtered_df.to_csv(
            sep=";",
            index=False,
        ).encode("cp1252")

        return HygieneMailingResponse(
            arquivo_gerado=new_file_name,
            conteudo=csv_content,
        )


    async def clean_mailing(self, request: CleanMailingRequest) -> HygieneMailingResponse:

        contents = await request.file.read()
        df = self._read_csv(contents)


        # Remove caracteres não numéricos
        df["CNPJ"] = df["CNPJ"].str.replace(r'\D', '', regex=True)
        df["CEP"] = df["CEP"].str.replace(r'\D', '', regex=True)

        # Adicona um ponto no CNPJ para formatar corretamente
        df["CNPJ"] += "."

        # Processa a coluna de telefone [converte para string, remove o prefixo "BR", filtra os números com 11 dígitos e remove duplicatas]
        df["Telefone 1"] = df["Telefone 1"].astype(str)
        df["Telefone 1"] = df["Telefone 1"].str[2:]
        df = df[df["Telefone 1"].str.len() == 11]
        df = df.drop_duplicates(subset="Telefone 1")

        # Cria novas colunas com base nas colunas existentes
        df["CEP_Número"] = df["CEP"] + df["Número"]
        df["Tipo_Endereço"] = df["Tipo"] + " " + df["Endereço"]

        # Remove caracteres não numéricos
        df["CEP_Número"] = df["CEP_Número"].str.replace(r"[/\.\- ]", "", regex=True)

        # Substitui os valores da coluna "Opção pelo MEI" com base na condição especificada
        df["Opção pelo MEI"] = np.where(df["Opção pelo MEI"] == "S", "MEI", "CNPJ")


        base_file_name = splitext(request.file.filename)[0]
        new_file_name = f"{base_file_name}_clean.csv"
        csv_content = df.to_csv(
            sep=";",
            index=False,
        ).encode("cp1252")

        return HygieneMailingResponse(
            arquivo_gerado=new_file_name,
            conteudo=csv_content,
        )


    async def mark_mailing_matches(self, request: MatchMailingRequest) -> HygieneMailingResponse:
        base_contents = await request.base_file.read()
        base_df = self._read_csv(base_contents)

        reference_contents = await request.reference_file.read()
        reference_df = self._read_csv(reference_contents)


        # Cria uma nova coluna "Cobertura" com base na correspondência com a coluna de referência
        base_df["Cobertura"] = np.where(base_df["CEP_Número"].isin(reference_df[reference_df.columns[0]]), "SIM", "NÃO")


        base_file_name = splitext(request.base_file.filename)[0]
        new_file_name = f"{base_file_name}_matched.csv"
        csv_content = base_df.to_csv(sep=";", index=False).encode("cp1252")

        return HygieneMailingResponse(
            arquivo_gerado=new_file_name,
            conteudo=csv_content,
        )


    async def concatenate_mailing(self, request: ConcatenateMailingRequest) -> HygieneMailingResponse:
        dataframes: List[pd.DataFrame] = []

        for file in request.files:
            contents = await file.read()
            dataframes.append(self._read_csv(contents))

        concatenated_df = pd.concat(dataframes, ignore_index=True)
        
        base_file_name = splitext(request.files[0].filename)[0]
        new_file_name = f"{base_file_name}_concatenated.csv"
        csv_content = concatenated_df.to_csv(sep=";", index=False).encode("cp1252")

        return HygieneMailingResponse(
            arquivo_gerado=new_file_name,
            conteudo=csv_content,
        )