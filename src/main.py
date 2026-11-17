import contextvars
import json
import logging
import os
import unicodedata
import uuid
from abc import ABC, abstractmethod
from datetime import UTC, datetime
from enum import StrEnum
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

def calcular_necessidades_obras(obras: list[Obra], tempo_max: int) -> list[Obra]:
    """Percorre as obras pela ordem dada e guarda as que ainda cabem no tempo."""
    selecionadas = []
    tempo_atual = 0
    for obra in obras:
        if tempo_atual + obra.minutos_visita <= tempo_max:
            selecionadas.append(obra)
            tempo_atual += obra.minutos_visita
    return selecionadas

class RotaMaisCurta(RoteiroStrategy):
    """Prioriza obras com menor tempo de visita para maximizar peças vistas."""

    def calcular_rota(self, obras: list[Obra], tempo_max: int) -> list[Obra]:
        obras_ordenadas = sorted(obras, key=lambda o: o.minutos_visita)
        return calcular_necessidades_obras(obras_ordenadas, tempo_max)


class RotaMenosCrowded(RoteiroStrategy):
    """Prioriza salas menos movimentadas (ordem inversa de ID/salas secundárias)."""

    def calcular_rota(self, obras: list[Obra], tempo_max: int) -> list[Obra]:
        obras_ordenadas = sorted(obras, key=lambda o: o.id, reverse=True)
        return calcular_necessidades_obras(obras_ordenadas, tempo_max)

class RotaFamiliar(RoteiroStrategy):
    """Prioriza obras com visita rápida (<= 8 min) adequadas para famílias."""

    def calcular_rota(self, obras: list[Obra], tempo_max: int) -> list[Obra]:
        obras_familiares = [o for o in obras if o.minutos_visita <= 8]
        return calcular_necessidades_obras(obras_familiares, tempo_max)

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


ESTRATEGIAS: dict[str, type[RoteiroStrategy]] = {
    "curta": RotaMaisCurta,
    "menos_crowded": RotaMenosCrowded,
    "familiar": RotaFamiliar,
}

def escolher_estrategia(nome: str) -> RoteiroStrategy:
    """Devolve a estratégia pedida, ou RotaMaisCurta se o nome for desconhecido."""
    if nome not in ESTRATEGIAS:
        logger.warning("Estratégia desconhecida '%s': a usar 'curta'", nome)
        return RotaMaisCurta()
    return ESTRATEGIAS[nome]()


def roteiro_para_dict(roteiro: Roteiro) -> dict:
    """Converte o roteiro no formato JSON devolvido pela API."""
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


@app.get("/roteiros")
def obter_roteiro(
    tempo: int = Query(60, gt=0),
    interesse: str | None = None,
    estrategia: str = "curta",
) -> dict:
    logger.info(
        "Roteiro pedido: tempo=%s interesse=%s estrategia=%s",
        tempo,
        interesse,
        estrategia,
    )
    roteiro = gerador_roteiro(
        carregar_museu_json(),
        tempo,
        interesse,
        strategy=escolher_estrategia(estrategia),
    )
    logger.info("Roteiro gerado: %s min", roteiro.calcular_tempo_total())
    return roteiro_para_dict(roteiro)


# --- Módulo B: Caça ao Tesouro (QR Code + Padrão Factory) ---

AUTOR_DESCONHECIDO = "Desconhecido"
ESTADO_TIPO_INVALIDO = "tipo_invalido"
ESTADO_NAO_DESBLOQUEADO = "nao_desbloqueado"


class EstadoQR(StrEnum):
    """Estados possíveis de um QR Code durante a validação."""

    PENDENTE = "pendente"
    VALIDADO = "validado"
    NULO = "nulo"
    VAZIO = "vazio"
    CORROMPIDO = "corrompido"
    REPETIDO = "repetido"


def _normalizar(texto: str) -> str:
    """Remove acentos, espaços laterais e diferenças de maiúsculas."""
    sem_acentos = "".join(
        c for c in unicodedata.normalize("NFD", texto) if not unicodedata.combining(c)
    )
    return sem_acentos.casefold().strip()


def _obra_por_codigo(codigo: str) -> Obra | None:
    return next((o for o in carregar_museu_json() if o.codigo_qr == codigo), None)


def _obra_seguinte(obra: Obra) -> Obra:
    """Próxima obra do acervo (circular), usada na pista de tipo 'qr'."""
    obras = carregar_museu_json()
    indice = next(i for i, o in enumerate(obras) if o.id == obra.id)
    return obras[(indice + 1) % len(obras)]


class QRCode:
    """QR Code lido pelo visitante: guarda o código e o estado da validação."""

    def __init__(self, codigo: Any = None, estado: EstadoQR = EstadoQR.PENDENTE):
        self.codigo = codigo
        self.estado = estado

    def validar(self) -> bool:
        """Valida o código. Só a primeira leitura de um QR válido devolve True."""
        if self.estado in (EstadoQR.VALIDADO, EstadoQR.REPETIDO):
            self.estado = EstadoQR.REPETIDO
        else:
            self.estado = self._classificar()
        logger.info(
            "QR Code validado",
            extra={
                "extra_data": {"codigo": str(self.codigo), "estado": str(self.estado)}
            },
        )
        return self.estado == EstadoQR.VALIDADO

    def _classificar(self) -> EstadoQR:
        if self.codigo is None:
            return EstadoQR.NULO
        if not isinstance(self.codigo, str):
            return EstadoQR.CORROMPIDO
        if not self.codigo.strip():
            return EstadoQR.VAZIO
        if _obra_por_codigo(self.codigo) is None:
            return EstadoQR.CORROMPIDO
        return EstadoQR.VALIDADO


class Desafio:
    """Desafio da caça ao tesouro: uma pergunta com uma resposta esperada."""

    tipo = "pergunta"

    def __init__(self, pergunta: str, resposta_correta: str):
        self.pergunta = pergunta
        self.resolvido = False
        self._resposta_correta = resposta_correta

    def verificarResposta(self, resposta: Any) -> bool:
        """Compara ignorando acentos, maiúsculas e espaços laterais."""
        correta = isinstance(resposta, str) and (
            _normalizar(resposta) == _normalizar(self._resposta_correta)
        )
        if correta:
            self.resolvido = True
        return correta


class DesafioPergunta(Desafio):
    """Pergunta sobre a obra (autor ou sala)."""

    tipo = "pergunta"


class DesafioQR(Desafio):
    """Pista que leva ao QR Code da obra seguinte."""

    tipo = "qr"


class DesafioBeacon(Desafio):
    """Aproximação a um beacon Bluetooth (simulado: o cliente envia o id)."""

    tipo = "beacon"


class DesafioFactory:
    """Factory Method: cria o tipo de desafio pedido para um QR já validado."""

    TIPOS = ("pergunta", "qr", "beacon")

    def criarDesafio(
        self, dadosQR: QRCode, tipo: str = DesafioPergunta.tipo
    ) -> Desafio:
        if tipo not in self.TIPOS:
            raise ValueError(f"Tipo de desafio desconhecido: {tipo}")
        obra = (
            _obra_por_codigo(dadosQR.codigo)
            if dadosQR.estado == EstadoQR.VALIDADO
            else None
        )
        if obra is None:
            raise ValueError("QRCode não validado: não é possível criar o desafio")

        criadores = {
            "pergunta": self._criar_pergunta,
            "qr": self._criar_qr,
            "beacon": self._criar_beacon,
        }
        return criadores[tipo](obra)

    @staticmethod
    def _criar_pergunta(obra: Obra) -> DesafioPergunta:
        if obra.autor and obra.autor != AUTOR_DESCONHECIDO:
            return DesafioPergunta(
                f"Quem é o autor da obra '{obra.titulo}'?", obra.autor
            )
        return DesafioPergunta(
            f"Em que sala está exposta a obra '{obra.titulo}'?", obra.sala
        )

    @staticmethod
    def _criar_qr(obra: Obra) -> DesafioQR:
        alvo = _obra_seguinte(obra)
        return DesafioQR(
            f"Pista: procura o QR Code da obra '{alvo.titulo}' ({alvo.sala}).",
            alvo.codigo_qr,
        )

    @staticmethod
    def _criar_beacon(obra: Obra) -> DesafioBeacon:
        return DesafioBeacon(
            f"Aproxima-te da obra '{obra.titulo}' ({obra.sala}). "
            "Qual o identificador do beacon detetado?",
            obra.codigo_qr.replace("-QR-", "-BCN-"),
        )


class Recompensa:
    """Medalha e desconto na loja/cafetaria conforme os desafios resolvidos."""

    # (mínimo de desafios resolvidos, medalha, desconto em %), do nível mais alto
    NIVEIS = ((10, "Ouro", 15), (6, "Prata", 10), (3, "Bronze", 5))

    def __init__(self, resolvidos: int = 0):
        self.resolvidos = max(0, resolvidos)
        self.medalha: str | None = None
        self.desconto = 0
        for minimo, nome, desconto in self.NIVEIS:
            if self.resolvidos >= minimo:
                self.medalha, self.desconto = nome, desconto
                break

    def como_dict(self) -> dict:
        return {
            "resolvidas": self.resolvidos,
            "medalha": self.medalha,
            "desconto_percentagem": self.desconto,
        }


class PedidoQR(BaseModel):
    codigo: Any = None
    sessao: str = "anonima"  # modo anónimo (US-04): sem PII, só um identificador
    tipo: str = DesafioPergunta.tipo


class PedidoResposta(BaseModel):
    codigo: str
    resposta: Any = None
    sessao: str = "anonima"


# Progresso de uma sessão: {codigo_qr: (QRCode, Desafio)}
Progresso = dict[str, tuple[QRCode, Desafio]]

# Progresso em memória, por sessão
_SESSOES: dict[str, Progresso] = {}

_STATUS_QR = {
    EstadoQR.NULO: 400,
    EstadoQR.VAZIO: 400,
    EstadoQR.CORROMPIDO: 422,
    EstadoQR.REPETIDO: 409,
}


def _recompensa_da_sessao(progresso: Progresso) -> Recompensa:
    return Recompensa(sum(1 for _, desafio in progresso.values() if desafio.resolvido))


def _qr_da_sessao(progresso: Progresso, codigo: Any) -> QRCode:
    """Reaproveita o QRCode já lido na sessão, para detetar leituras repetidas."""
    if isinstance(codigo, str) and codigo in progresso:
        return progresso[codigo][0]
    return QRCode(codigo)


def _erro_validacao(status_code: int, estado: str) -> HTTPException:
    return HTTPException(
        status_code=status_code,
        detail={"valido": False, "estado": str(estado)},
    )


def _como_pista(obra: Obra, desafio: Desafio) -> dict:
    return {
        "codigo_qr": obra.codigo_qr,
        "obra_id": obra.id,
        "titulo": obra.titulo,
        "sala": obra.sala,
        "tipo": desafio.tipo,
        "pergunta": desafio.pergunta,
        "resolvido": desafio.resolvido,
    }

@app.post("/qr/validar")
def validar_qr(pedido: PedidoQR) -> dict:
    """Valida o QR Code lido e desbloqueia o desafio da obra (US-03)."""
    if pedido.tipo not in DesafioFactory.TIPOS:
        raise _erro_validacao(400, ESTADO_TIPO_INVALIDO)
    logger.info("Validação de QR pedida: codigo=%r", pedido.codigo)  # NUEVO

    progresso = _SESSOES.setdefault(pedido.sessao, {})
    qr = _qr_da_sessao(progresso, pedido.codigo)
    if not qr.validar():
        logger.warning(
            "QR rejeitado: codigo=%r estado=%s", pedido.codigo, qr.estado
        )
        raise _erro_validacao(_STATUS_QR[qr.estado], qr.estado)

    desafio = DesafioFactory().criarDesafio(qr, pedido.tipo)
    progresso[qr.codigo] = (qr, desafio)
    obra = _obra_por_codigo(qr.codigo)
    logger.info("QR validado: codigo=%s obra=%s", qr.codigo, obra.id)
    return {
        "valido": True,
        "estado": qr.estado,
        "codigo": qr.codigo,
        "obra": {"id": obra.id, "titulo": obra.titulo, "sala": obra.sala},
        "desafio": {
            "tipo": desafio.tipo,
            "pergunta": desafio.pergunta,
            "resolvido": desafio.resolvido,
        },
    }


@app.post("/desafios/responder")
def responder_desafio(pedido: PedidoResposta) -> dict:
    """Verifica a resposta a um desafio desbloqueado e devolve a recompensa."""
    progresso = _SESSOES.get(pedido.sessao, {})
    if pedido.codigo not in progresso:
        raise HTTPException(
            status_code=404, detail={"estado": ESTADO_NAO_DESBLOQUEADO}
        )
    _, desafio = progresso[pedido.codigo]
    correta = desafio.verificarResposta(pedido.resposta)
    return {
        "correta": correta,
        "resolvido": desafio.resolvido,
        "recompensa": _recompensa_da_sessao(progresso).como_dict(),
    }


@app.get("/pistas")
def listar_pistas(sessao: str = "anonima") -> dict:
    """Lista as pistas desbloqueadas na sessão e a recompensa atual."""
    progresso = _SESSOES.get(sessao, {})
    obras = carregar_museu_json()
    obras_por_codigo = {obra.codigo_qr: obra for obra in obras}
    pistas = [
        _como_pista(obras_por_codigo[codigo], desafio)
        for codigo, (_, desafio) in progresso.items()
    ]
    return {
        "sessao": sessao,
        "total_obras": len(obras),
        "desbloqueadas": len(pistas),
        "recompensa": _recompensa_da_sessao(progresso).como_dict(),
        "pistas": pistas,
    }
