"""
Funcionalidade: TRIACETINA.

Fluxo da tela (uma unica pagina, /triacetina):
  1. Ao abrir  -> mostra o STATUS do banco + campo para informar a ESTACAO.
                  Nao popula leitura ainda (espera o usuario buscar).
  2. Buscar    -> consulta a ultima leitura DAQUELA estacao e popula a tela.
                  So depois da busca aparece o formulario de insercao.
  3. Inserir   -> grava uma nova leitura AMARRADA a estacao buscada.

Por enquanto os dados sao de EXEMPLO (em memoria). Os pontos onde entra o
SQL Server estao marcados com  # TODO SQL SERVER.
"""

from datetime import datetime

from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

# prefix: todas as rotas aqui comecam com /triacetina
router = APIRouter(prefix="/triacetina", tags=["triacetina"])

templates = Jinja2Templates(directory="templates")

MAX_LEN = 100

# --------------------------------------------------------------------------
# Dados de EXEMPLO em memoria (serao substituidos por consultas ao SQL Server).
# Estrutura de uma leitura (campos de exemplo - ajuste conforme o processo real):
#   estacao, teor (valor), unidade, lote, quando
# Guardamos as leituras por estacao para simular a busca.
# --------------------------------------------------------------------------
leituras_por_estacao = {
    "EST-01": [
        {"teor": "99.2", "unidade": "%", "lote": "L-2241", "quando": "2026-10-13 14:02"},
    ],
    "EST-02": [
        {"teor": "98.7", "unidade": "%", "lote": "L-2242", "quando": "2026-10-13 14:03"},
    ],
}


def _banco_online():
    """Verifica a conexao com o banco.

    POR ENQUANTO: simulado (retorna sempre True).
    # TODO SQL SERVER: trocar por um teste real de conexao (abrir e fechar
    # uma conexao pyodbc, retornando True/False).
    """
    return True


def _ultima_leitura(estacao):
    """Retorna a ultima leitura da estacao, ou None.

    POR ENQUANTO: busca no dicionario em memoria.
    # TODO SQL SERVER: trocar por um SELECT ... WHERE estacao = ? ORDER BY data DESC
    # (query parametrizada - nunca concatenar o valor da estacao na SQL).
    """
    registros = leituras_por_estacao.get(estacao.strip().upper())
    if registros:
        return registros[0]
    return None


def _limpar(texto, campo):
    """Validacao minima de entrada (nunca confiar no que vem do browser)."""
    if texto is None:
        raise ValueError("O campo '" + campo + "' e obrigatorio.")
    texto = texto.strip()
    if not texto:
        raise ValueError("O campo '" + campo + "' nao pode ficar vazio.")
    if len(texto) > MAX_LEN:
        raise ValueError("O campo '" + campo + "' excede " + str(MAX_LEN) + " caracteres.")
    return texto


def _render(request, estacao=None, leitura=None, erro=None, ok=False):
    """Monta a tela com o estado atual."""
    return templates.TemplateResponse(
        "triacetina/home.html",
        {
            "request": request,
            "banco_online": _banco_online(),
            "estacao": estacao,          # estacao buscada (None = ainda nao buscou)
            "leitura": leitura,          # ultima leitura da estacao (None = nao achou)
            "erro": erro,
            "ok": ok,
        },
    )


@router.get("")
def home(request: Request):
    """Abre a pagina: so status do banco + campo de busca. Nao popula leitura."""
    return _render(request)


@router.get("/buscar")
def buscar(request: Request, estacao: str = ""):
    """Busca a ultima leitura da estacao informada e popula a tela."""
    if not estacao.strip():
        return _render(request, erro="Informe a estacao para buscar.")
    leitura = _ultima_leitura(estacao)
    return _render(request, estacao=estacao.strip().upper(), leitura=leitura)


@router.post("")
def inserir(request: Request, estacao: str = Form(...), teor: str = Form(...),
            unidade: str = Form(...), lote: str = Form(...)):
    """Grava uma nova leitura AMARRADA a estacao buscada."""
    try:
        estacao = _limpar(estacao, "estacao").upper()
        teor = _limpar(teor, "teor")
        unidade = _limpar(unidade, "unidade")
        lote = _limpar(lote, "lote")
    except ValueError as e:
        leitura = _ultima_leitura(estacao) if estacao else None
        return _render(request, estacao=estacao, leitura=leitura, erro=str(e))

    nova = {
        "teor": teor,
        "unidade": unidade,
        "lote": lote,
        "quando": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    # POR ENQUANTO: grava em memoria.
    # TODO SQL SERVER: trocar por INSERT ... (query parametrizada).
    leituras_por_estacao.setdefault(estacao, []).insert(0, nova)

    # Post/Redirect/Get: volta para a busca ja mostrando a leitura nova
    return RedirectResponse(url="/triacetina/buscar?estacao=" + estacao, status_code=303)