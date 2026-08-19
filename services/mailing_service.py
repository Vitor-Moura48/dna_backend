import pandas as pd
import io
from os.path import splitext
from data.dtos.mailing.mailing_request import HygieneMailingRequest
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