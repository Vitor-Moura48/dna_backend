from http import HTTPStatus
from fastapi import APIRouter, Depends, Response, UploadFile, File
from services.mailing_service import MailingService
from data.dtos.mailing.mailing_request import (
    HygieneMailingRequest,
    CleanMailingRequest,
    MatchMailingRequest,
    ConcatenateMailingRequest,
)
from data.dtos.mailing.mailing_response import HygieneMailingResponse

router = APIRouter()

@router.post("/", status_code=HTTPStatus.OK)
async def hygiene_mailing(
    base_file: UploadFile = File(...),
    filter_file: UploadFile = File(...),
    mailing_service: MailingService = Depends()
    ):

    # Monta o DTO
    request = HygieneMailingRequest(
        base_file=base_file,
        filter_file=filter_file,
    )
    
    # Valida
    request.validate_input()
    
    result: HygieneMailingResponse = await mailing_service.hygiene_mailing(request)

    return Response(
        content=result.conteudo,
        media_type="application/octet-stream",
        status_code=HTTPStatus.OK,
        headers={
            "Content-Disposition": f'attachment; filename="{result.arquivo_gerado}"',
        },
    )


@router.post("/clean", status_code=HTTPStatus.OK)
async def clean_mailing(
    file: UploadFile = File(...),
    mailing_service: MailingService = Depends()
    ):

    request = CleanMailingRequest(file=file)
    request.validate_input()

    result: HygieneMailingResponse = await mailing_service.clean_mailing(request)

    return Response(
        content=result.conteudo,
        media_type="application/octet-stream",
        status_code=HTTPStatus.OK,
        headers={
            "Content-Disposition": f'attachment; filename="{result.arquivo_gerado}"',
        },
    )


@router.post("/match", status_code=HTTPStatus.OK)
async def mark_mailing_matches(
    base_file: UploadFile = File(...),
    reference_file: UploadFile = File(...),
    mailing_service: MailingService = Depends()
    ):

    request = MatchMailingRequest(
        base_file=base_file,
        reference_file=reference_file,
    )
    request.validate_input()

    result: HygieneMailingResponse = await mailing_service.mark_mailing_matches(request)

    return Response(
        content=result.conteudo,
        media_type="application/octet-stream",
        status_code=HTTPStatus.OK,
        headers={
            "Content-Disposition": f'attachment; filename="{result.arquivo_gerado}"',
        },
    )


@router.post("/concatenate", status_code=HTTPStatus.OK)
async def concatenate_mailing(
    files: list[UploadFile] = File(
        ...,
        json_schema_extra={"items": {"type": "string", "format": "binary"}},
    ),
    mailing_service: MailingService = Depends()
    ):

    request = ConcatenateMailingRequest(files=files)
    request.validate_input()

    result: HygieneMailingResponse = await mailing_service.concatenate_mailing(request)

    return Response(
        content=result.conteudo,
        media_type="application/octet-stream",
        status_code=HTTPStatus.OK,
        headers={
            "Content-Disposition": f'attachment; filename="{result.arquivo_gerado}"',
        },
    )