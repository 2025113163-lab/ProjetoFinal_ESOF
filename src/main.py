import contextvars
import json
import logging
import os
import uuid
from abc import ABC, abstractmethod
from datetime import UTC, datetime

from fastapi import FastAPI, Query, Request

request_id_ctx: contextvars.ContextVar[str] = contextvars.ContextVar(
    "request_id", default="system"
)


class JSONFormatter(logging.Formatter):
    """Formata os registos de log em JSON estruturado com request_id."""

    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "request_id": request_id_ctx.get(),
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "extra_data"):
            log_record.update(record.extra_data)
        return json.dumps(log_record, ensure_ascii=False)


logger = logging.getLogger("mnsr_digital")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)

app = FastAPI(title="MNSR Digital API")


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    req_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    token = request_id_ctx.set(req_id)
    logger.info(
        "Pedido HTTP recebido",
        extra={"extra_data": {"method": request.method, "path": request.url.path}},
    )
    try:
        response = await call_next(request)
        response.headers["X-Request-ID"] = req_id
        logger.info(
            "Resposta HTTP enviada",
            extra={
                "extra_data": {
                    "path": request.url.path,
                    "status_code": response.status_code,
                }
            },
        )
        return response
    finally:
        request_id_ctx.reset(token)


@app.get("/health")
def health() -> dict:
    logger.info("Verificação de estado (/health) executada com sucesso")
    return {"status": "ok"}


class Obra:
    def __init__(
        self,
        id: int,
        titulo: str,
        autor: str,
        minutos_visita: int,
        sala: str = "",
        tema: str = "",
        codigo_qr: str = "",
    ):
        self.id = id
        self.titulo = titulo
        self.autor = autor
        self.minutos_visita = minutos_visita
        self.sala = sala
        self.tema = tema
        self.codigo_qr = codigo_qr

    def __repr__(self):
        return (
            f"Obra(id={self.id}, titulo='{self.titulo}', "
            f"tema='{self.tema}', minutos_visita={self.minutos_visita})"
        )


class Sala:
    def __init__(self, nome: str):
        self.nome = nome
        self.obras: list[Obra] = []

    def adicionar_obra(self, obra: Obra):
        self.obras.append(obra)

    def __repr__(self):
        return f"Sala(nome='{self.nome}', obras={self.obras})"


class RoteiroStrategy(ABC):
    @abstractmethod
    def calcular_rota(self, obras: list[Obra], tempo_max: int) -> list[Obra]:
        pass


class RotaMaisCurta(RoteiroStrategy):
    """Prioriza obras com menor tempo de visita para maximizar peças vistas."""

    def calcular_rota(self, obras: list[Obra], tempo_max: int) -> list[Obra]:
        obras_ordenadas = sorted(obras, key=lambda o: o.minutos_visita)
        selecionadas = []
        tempo_atual = 0
        for obra in obras_ordenadas:
            if tempo_atual + obra.minutos_visita <= tempo_max:
                selecionadas.append(obra)
                tempo_atual += obra.minutos_visita
        return selecionadas


class RotaMenosCrowded(RoteiroStrategy):
    """Prioriza salas menos movimentadas (ordem inversa de ID/salas secundárias)."""

    def calcular_rota(self, obras: list[Obra], tempo_max: int) -> list[Obra]:
        obras_ordenadas = sorted(obras, key=lambda o: o.id, reverse=True)
        selecionadas = []
        tempo_atual = 0
        for obra in obras_ordenadas:
            if tempo_atual + obra.minutos_visita <= tempo_max:
                selecionadas.append(obra)
                tempo_atual += obra.minutos_visita
        return selecionadas


class RotaFamiliar(RoteiroStrategy):
    """Prioriza obras com visita rápida (<= 8 min) adequadas para famílias."""

    def calcular_rota(self, obras: list[Obra], tempo_max: int) -> list[Obra]:
        obras_familiares = [o for o in obras if o.minutos_visita <= 8]
        selecionadas = []
        tempo_atual = 0
        for obra in obras_familiares:
            if tempo_atual + obra.minutos_visita <= tempo_max:
                selecionadas.append(obra)
                tempo_atual += obra.minutos_visita
        return selecionadas


class Roteiro:
    def __init__(self, nome: str, strategy: RoteiroStrategy | None = None):
        self.nome = nome
        self.obras: list[Obra] = []
        self.strategy = strategy or RotaMaisCurta()

    def adicionar_obra(self, obra: Obra):
        self.obras.append(obra)

    def calcular_tempo_total(self) -> int:
        return sum(obra.minutos_visita for obra in self.obras)

    def __repr__(self):
        return f"Roteiro(nome='{self.nome}', tempo_total={self.calcular_tempo_total()})"


def carregar_museu_json(caminho_ficheiro: str = "data/museu.json") -> list[Obra]:
    if not os.path.exists(caminho_ficheiro):
        logger.warning(
            "Ficheiro de dados não encontrado",
            extra={"extra_data": {"caminho": caminho_ficheiro}},
        )
        return []

    with open(caminho_ficheiro, "r", encoding="utf-8") as f:
        dados = json.load(f)

    lista_obras = []
    for item in dados:
        obra = Obra(
            id=item["id"],
            titulo=item.get("titulo") or item.get("Titulo", ""),
            autor=item.get("autor", "Desconhecido"),
            minutos_visita=item["minutos_visita"],
            sala=item.get("sala", ""),
            tema=item.get("tema", ""),
            codigo_qr=item.get("codigo_qr") or item.get("codigoQR", ""),
        )
        lista_obras.append(obra)

    return lista_obras


def gerador_roteiro(
    obras: list[Obra],
    tempo_max: int,
    interesse: str | None = None,
    strategy: RoteiroStrategy | None = None,
) -> Roteiro:
    estrategia = strategy or RotaMaisCurta()
    roteiro = Roteiro(
        nome=f"Roteiro {interesse or 'Geral'} ({tempo_max} min)",
        strategy=estrategia,
    )

    if tempo_max <= 0 or not obras:
        logger.warning(
            "Roteiro vazio por parâmetros inválidos ou lista de obras vazia",
            extra={"extra_data": {"tempo_max": tempo_max, "total_obras": len(obras)}},
        )
        return roteiro

    obras_filtradas = obras
    if interesse:
        termo = interesse.lower()
        obras_filtradas = [
            o
            for o in obras
            if termo in o.tema.lower() or termo in o.sala.lower()
        ]

    roteiro.obras = estrategia.calcular_rota(obras_filtradas, tempo_max)
    logger.info(
        "Roteiro calculado com sucesso",
        extra={
            "extra_data": {
                "estrategia": estrategia.__class__.__name__,
                "tempo_max": tempo_max,
                "interesse": interesse,
                "obras_selecionadas": len(roteiro.obras),
                "tempo_total": roteiro.calcular_tempo_total(),
            }
        },
    )
    return roteiro


@app.get("/roteiros")
def obter_roteiro(
    tempo: int = Query(60, gt=0),
    interesse: str | None = None,
    estrategia: str = "curta",
) -> dict:
    obras = carregar_museu_json()
    mapa_estrategias = {
        "curta": RotaMaisCurta(),
        "menos_crowded": RotaMenosCrowded(),
        "familiar": RotaFamiliar(),
    }
    strat = mapa_estrategias.get(estrategia, RotaMaisCurta())
    roteiro = gerador_roteiro(obras, tempo, interesse, strategy=strat)
    return {
        "nome": roteiro.nome,
        "tempo_total": roteiro.calcular_tempo_total(),
        "obras": [
            {
                "id": o.id,
                "titulo": o.titulo,
                "autor": o.autor,
                "sala": o.sala,
                "tema": o.tema,
                "minutos_visita": o.minutos_visita,
            }
            for o in roteiro.obras
        ],
    }