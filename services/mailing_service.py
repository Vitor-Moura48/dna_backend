import pandas as pd
import io
from os.path import basename, splitext, dirname, join
from data.dtos.mailing.mailing_request import HygieneMailingRequest

class MailingService:
    def __init__(self):
        pass

    async def hygiene_mailing(self, request: HygieneMailingRequest) -> dict:
        
        if request.base_file:

            # Lê o conteúdo do arquivo enviado como bytes
            contents = await request.base_file.read()
            # Lê direto dos bytes e decodifica via C-Engine
            base_df = pd.read_csv(io.BytesIO(contents), sep=";", encoding="cp1252")

            base_file_name = splitext(request.base_file.filename)[0]

        else:
            base_df = pd.read_csv(request.base_file_path, sep=";", encoding="cp1252") # padrao de encoding para essa regra de négocio
            base_file_name = splitext(basename(request.base_file_path))[0]  # Extrai o nome do arquivo do caminho
           

        if request.filter_file:
            contents = await request.filter_file.read()
            filter_df = pd.read_csv(io.BytesIO(contents), sep=";", encoding="utf-8")

        else:
            filter_df = pd.read_csv(request.filter_file_path, sep=";", encoding="utf-8") # padrao de encoding para essa regra de négocio


        # Converte as colunas de número para string
        base_df["DDDNUM"] = base_df["DDDNUM"].astype(str)
        filter_df["number"] = filter_df["number"].astype(str)

        # Remove o prefixo "BR" da coluna filter_df
        filter_df["number"] = filter_df["number"].str[2:]

        # Filtra os registros do base_df que não estão presentes no filter_df
        filtered_df = base_df[~base_df["DDDNUM"].isin(filter_df["number"])]

        # Retorna o DataFrame filtrado como um novo arquivo CSV
        prefix, num = base_file_name.rsplit("_", 1)
        new_file_name = f"{prefix}_{int(num) + 1}.csv" # Incrementa o número do arquivo

        # Salva o DataFrame filtrado em um novo arquivo CSV
        new_file_path = join(request.output_dir, new_file_name)
        filtered_df.to_csv(new_file_path, sep=";", index=False, encoding="cp1252")

        return {
            "arquivo_gerado": new_file_name,
            "linhas_base": len(base_df),
            "linhas_filtro": len(filter_df),
            "linhas_removidas": len(base_df) - len(filtered_df),
            "linhas_finais": len(filtered_df),
        }