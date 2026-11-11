import contextvars, json, logging, os, uuid, unicodedata

from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import Any
from fastapi import FastAPI, HTTPException, Query, Request
from pydantic import BaseModel


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



# --- Caça ao Tesouro (QR Code + Padrão Factory) ---


def _normalizar(texto: str) -> str:
    """Remove acentos, espaços laterais e diferenças de maiúsculas."""
    sem_acentos = "".join(
        c for c in unicodedata.normalize("NFD", texto) if not unicodedata.combining(c)
    )
    return sem_acentos.casefold().strip()


def _obra_por_codigo(codigo: str) -> Obra | None:
    return next((o for o in carregar_museu_json() if o.codigo_qr == codigo), None)


class QRCode:

    def __init__(self, codigo: Any = None, estado: str = "pendente"):
        self.codigo = codigo
        self.estado = estado

    def validar(self) -> bool:
        if self.estado in ("validado", "repetido"):
            self.estado = "repetido"
        elif self.codigo is None:
            self.estado = "nulo"
        elif isinstance(self.codigo, str) and not self.codigo.strip():
            self.estado = "vazio"
        elif not isinstance(self.codigo, str) or _obra_por_codigo(self.codigo) is None:
            self.estado = "corrompido"
        else:
            self.estado = "validado"
        logger.info(
            "QR Code validado",
            extra={"extra_data": {"codigo": str(self.codigo), "estado": self.estado}},
        )
        return self.estado == "validado"


class Desafio:
    def __init__(self, pergunta: str, resposta_correta: str):
        self.pergunta = pergunta
        self.resolvido = False
        self._resposta_correta = resposta_correta

    def verificarResposta(self, resposta: str) -> bool:
        correta = isinstance(resposta, str) and (
            _normalizar(resposta) == _normalizar(self._resposta_correta)
        )
        if correta:
            self.resolvido = True
        return correta


class DesafioFactory:
    def criarDesafio(self, dadosQR: QRCode) -> Desafio:
        obra = _obra_por_codigo(dadosQR.codigo) if dadosQR.estado == "validado" else None
        if obra is None:
            raise ValueError("QRCode não validado: não é possível criar o desafio")
        if obra.autor and obra.autor != "Desconhecido":
            return Desafio(f"Quem é o autor da obra '{obra.titulo}'?", obra.autor)
        return Desafio(f"Em que sala está exposta a obra '{obra.titulo}'?", obra.sala)


class PedidoQR(BaseModel):
    codigo: Any = None
    sessao: str = "anonima"  # modo anónimo (US-04): sem PII, só um identificador


# Progresso em memória por sessão: {sessao: {codigo_qr: (QRCode, Desafio)}}
_SESSOES: dict[str, dict[str, tuple[QRCode, Desafio]]] = {}

_STATUS_QR = {"nulo": 400, "vazio": 400, "corrompido": 422, "repetido": 409}


@app.post("/qr/validar")
def validar_qr(pedido: PedidoQR) -> dict:
    progresso = _SESSOES.setdefault(pedido.sessao, {})
    existente = progresso.get(pedido.codigo) if isinstance(pedido.codigo, str) else None
    qr = existente[0] if existente else QRCode(pedido.codigo)

    if not qr.validar():
        raise HTTPException(
            status_code=_STATUS_QR[qr.estado],
            detail={"valido": False, "estado": qr.estado},
        )

    desafio = DesafioFactory().criarDesafio(qr)
    progresso[qr.codigo] = (qr, desafio)
    obra = _obra_por_codigo(qr.codigo)
    return {
        "valido": True,
        "estado": qr.estado,
        "codigo": qr.codigo,
        "obra": {"id": obra.id, "titulo": obra.titulo, "sala": obra.sala},
        "desafio": {"pergunta": desafio.pergunta, "resolvido": desafio.resolvido},
    }


@app.get("/pistas")
def listar_pistas(sessao: str = "anonima") -> dict:
    progresso = _SESSOES.get(sessao, {})
    pistas = []
    for codigo, (_, desafio) in progresso.items():
        obra = _obra_por_codigo(codigo)
        pistas.append(
            {
                "codigo_qr": codigo,
                "obra_id": obra.id,
                "titulo": obra.titulo,
                "sala": obra.sala,
                "pergunta": desafio.pergunta,
                "resolvido": desafio.resolvido,
            }
        )
    return {
        "sessao": sessao,
        "total_obras": len(carregar_museu_json()),
        "desbloqueadas": len(pistas),
        "pistas": pistas,
    }