import pandas as pd
import io, numpy as np
from os.path import splitext
from data.dtos.mailing.mailing_request import HygieneMailingRequest, CleanMailingRequest
from data.dtos.mailing.mailing_response import HygieneMailingResponse

class MailingService:
    def __init__(self):
        pass

    async def hygiene_mailing(self, request: HygieneMailingRequest) -> HygieneMailingResponse:

        base_contents = await request.base_file.read()
        base_df = pd.read_csv(
            io.BytesIO(base_contents),
            sep=";",
            encoding="cp1252",
        )

        filter_contents = await request.filter_file.read()
        filter_df = pd.read_csv(
            io.BytesIO(filter_contents),
            sep=";",
            encoding="utf-8",
        )


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
        df = pd.read_csv(
            io.BytesIO(contents),
            sep=";",
            encoding="utf-8",
        )


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