import pandas as pd
import io
from os.path import splitext
from typing import List
from fastapi import HTTPException
from data.dtos.mailing.mailing_request import (
    SingleFileRequest,
    TwoFilesRequest,
    MultipleFilesRequest,
)
from data.dtos.mailing.mailing_response import HygieneMailingResponse
from services.mailing.mailing_transformation import (
    clean_mailing_transformation,
    concatenate_mailing_transformation,
    hygiene_mailing_transformation,
    mark_mailing_matches_transformation,
    pre_prospecting_transformation,
)

class MailingService:
    def __init__(self):
        pass

    @staticmethod
    def _read_csv(contents: bytes, file_name: str = "", dtype=str) -> pd.DataFrame:
        for encoding in ("utf-8-sig", "cp1252", "latin1", "utf-16"):
            try:
                return pd.read_csv(
                    io.BytesIO(contents),
                    sep=";",
                    encoding=encoding,
                    dtype=dtype
                )
            except UnicodeError:
                continue
            except (pd.errors.EmptyDataError, pd.errors.ParserError) as error:
                raise HTTPException(
                    status_code=400,
                    detail=f"Não foi possível ler o arquivo '{file_name}': {error}.",
                ) from error

        # Mantem a importacao funcionando quando houver bytes isolados corrompidos.
        return pd.read_csv(
            io.BytesIO(contents),
            sep=";",
            encoding="cp1252",
            encoding_errors="replace",
            dtype=dtype
        )

    @staticmethod
    def _validate_columns(
        dataframe: pd.DataFrame,
        required_columns: List[str],
        file_name: str,
    ) -> None:
        missing_columns = [
            column for column in required_columns if column not in dataframe.columns
        ]
        if missing_columns:
            missing = ", ".join(missing_columns)
            raise HTTPException(
                status_code=400,
                detail=(
                    f"O arquivo '{file_name}' não possui as colunas obrigatórias: "
                    f"{missing}."
                ),
            )

    async def hygiene_mailing(self, request: TwoFilesRequest) -> HygieneMailingResponse:

        base_contents = await request.first_file.read()
        base_df = self._read_csv(base_contents, file_name=request.first_file.filename)
        self._validate_columns(base_df, ["DDDNUM"], request.first_file.filename)

        filter_contents = await request.second_file.read()
        filter_df = self._read_csv(filter_contents, file_name=request.second_file.filename)
        self._validate_columns(filter_df, ["number"], request.second_file.filename)

        filtered_df = hygiene_mailing_transformation(base_df, filter_df)


        # Retorna o DataFrame filtrado como um novo arquivo CSV
        base_file_name = splitext(request.first_file.filename)[0]
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


    async def clean_mailing(self, request: SingleFileRequest) -> HygieneMailingResponse:

        contents = await request.file.read()
        df = self._read_csv(contents, file_name=request.file.filename)
        self._validate_columns(
            df,
            ["CNPJ", "CEP", "Telefone 1", "Número", "Tipo", "Endereço", "Opção pelo MEI"],
            request.file.filename,
        )


        df = clean_mailing_transformation(df)


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


    async def pre_prospecting(self, request: SingleFileRequest) -> HygieneMailingResponse:
        contents = await request.file.read()
        df = self._read_csv(contents, file_name=request.file.filename)
        self._validate_columns(
            df,
            ["CNPJ", "CEP", "Telefone 1"],
            request.file.filename,
        )


        result_df = pre_prospecting_transformation(df)


        base_file_name = splitext(request.file.filename)[0]
        new_file_name = f"{base_file_name}_pre_prospecting.csv"
        csv_content = result_df.to_csv(sep=";", index=False).encode("cp1252")

        return HygieneMailingResponse(
            arquivo_gerado=new_file_name,
            conteudo=csv_content,
        )


    async def mark_mailing_matches(self, request: TwoFilesRequest) -> HygieneMailingResponse:
        base_contents = await request.first_file.read()
        base_df = self._read_csv(base_contents, file_name=request.first_file.filename)
        self._validate_columns(base_df, ["CEP_Número"], request.first_file.filename)

        reference_contents = await request.second_file.read()
        reference_df = self._read_csv(
            reference_contents,
            file_name=request.second_file.filename,
        )
        
        if reference_df.empty or len(reference_df.columns) == 0:
            raise HTTPException(
                status_code=400,
                detail=f"O arquivo '{request.second_file.filename}' não possui colunas.",
            )


        base_df = mark_mailing_matches_transformation(base_df, reference_df)


        base_file_name = splitext(request.first_file.filename)[0]
        new_file_name = f"{base_file_name}_matched.csv"
        csv_content = base_df.to_csv(sep=";", index=False).encode("cp1252")

        return HygieneMailingResponse(
            arquivo_gerado=new_file_name,
            conteudo=csv_content,
        )


    async def concatenate_mailing(self, request: MultipleFilesRequest) -> HygieneMailingResponse:
        dataframes: List[pd.DataFrame] = []

        for file in request.files:
            contents = await file.read()
            dataframes.append(self._read_csv(contents, file_name=file.filename))

        concatenated_df = concatenate_mailing_transformation(dataframes)
        
        base_file_name = splitext(request.files[0].filename)[0]
        new_file_name = f"{base_file_name}_concatenated.csv"
        csv_content = concatenated_df.to_csv(sep=";", index=False).encode("cp1252")

        return HygieneMailingResponse(
            arquivo_gerado=new_file_name,
            conteudo=csv_content,
        )