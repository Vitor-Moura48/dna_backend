import os
import sys
import uvicorn
from fastapi import FastAPI

from controllers import health_controller, mailing_controller, utility_controller
from handlers.exception_handlers import global_exception_handler

# Redireciona a saída padrão e a saída de erro para /dev/null (Para rodar em modo windowed sem abrir o console)
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w", encoding="utf-8")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w", encoding="utf-8")

app = FastAPI(
    title="DNA Backend",
    version="0.1.0",
    description="API de automatização de processos de dados",
)

# Inclui os routers das controllers
app.include_router(mailing_controller.router, prefix="/mailing", tags=["Mailing"])
app.include_router (utility_controller.router, prefix="/utility", tags=["Utility"])
app.include_router(health_controller.router, prefix="/health", tags=["Health"])

# Adiciona o manipulador de exceções global
app.add_exception_handler(Exception, global_exception_handler)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=6464)