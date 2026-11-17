"""Módulo D: indicador de afluência por sala (padrão Observer).

`AfluenciaSala` é o Subject: mantém a contagem de visitantes de uma sala e
notifica os observadores sempre que o limiar de lotação é atravessado
(em qualquer um dos sentidos). Não depende de FastAPI.
"""

import logging
from abc import ABC, abstractmethod

logger = logging.getLogger("mnsr_digital")


class ObservadorAfluencia(ABC):
    """Interface Observer: quem quer saber quando a lotação de uma sala muda."""

    @abstractmethod
    def atualizar(self, afluencia: "AfluenciaSala") -> None:
        pass


class AfluenciaSala:
    """Subject: contagem de visitantes de uma sala face ao limite máximo."""

    def __init__(self, sala: str, limite_maximo: int):
        if limite_maximo <= 0:
            raise ValueError("limite_maximo tem de ser maior que zero")
        self.sala = sala
        self.limite_maximo = limite_maximo
        self.visitantes_atuais = 0
        self._observadores: list[ObservadorAfluencia] = []
        self._lotada = False

    @property
    def lotada(self) -> bool:
        return self._lotada

    def adicionar_observador(self, observador: ObservadorAfluencia) -> None:
        if observador not in self._observadores:
            self._observadores.append(observador)

    def remover_observador(self, observador: ObservadorAfluencia) -> None:
        if observador in self._observadores:
            self._observadores.remove(observador)

    def registar_entrada(self) -> None:
        self.visitantes_atuais += 1
        self.notificar_limiar()

    def registar_saida(self) -> None:
        if self.visitantes_atuais == 0:
            logger.warning(
                "Saída ignorada: sala já está vazia",
                extra={"extra_data": {"sala": self.sala}},
            )
            return
        self.visitantes_atuais -= 1
        self.notificar_limiar()

    def notificar_limiar(self) -> None:
        """Notifica os observadores só quando o estado 'lotada' muda."""
        lotada = self.visitantes_atuais >= self.limite_maximo
        if lotada == self._lotada:
            return
        self._lotada = lotada
        logger.info(
            "Limiar de afluência atravessado",
            extra={
                "extra_data": {
                    "sala": self.sala,
                    "visitantes_atuais": self.visitantes_atuais,
                    "limite_maximo": self.limite_maximo,
                    "lotada": lotada,
                }
            },
        )
        for observador in list(self._observadores):
            observador.atualizar(self)


class NotificadorApp(ObservadorAfluencia):
    """Observer concreto: gera a mensagem a enviar à app dos visitantes."""

    def __init__(self):
        self.mensagens: list[str] = []

    def atualizar(self, afluencia: AfluenciaSala) -> None:
        if afluencia.lotada:
            msg = f"{afluencia.sala} está cheia. Sugerimos visitar outra sala."
        else:
            msg = f"{afluencia.sala} já tem espaço disponível."
        self.mensagens.append(msg)
