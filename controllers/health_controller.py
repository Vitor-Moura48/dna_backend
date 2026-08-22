from fastapi import APIRouter, Response 
from http import HTTPStatus

router = APIRouter()

@router.get("/", status_code=HTTPStatus.OK)
@router.head("/", status_code=HTTPStatus.OK)
async def health_check():
    return Response(status_code=HTTPStatus.OK)