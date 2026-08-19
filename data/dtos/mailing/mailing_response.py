from pydantic import BaseModel, Field


class HygieneMailingResponse(BaseModel):
    arquivo_gerado: str = Field(description="Nome do arquivo CSV gerado")
    conteudo: bytes = Field(description="Conteúdo binário do arquivo para download")
