"""
POC - Servidor FastAPI (multi-funcionalidade).
"""

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from triacetina.rotas import router as triacetina_router

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(triacetina_router)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def raiz():
    return RedirectResponse(url="/triacetina")