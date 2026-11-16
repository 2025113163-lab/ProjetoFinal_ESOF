import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from src.main import (
    AUTOR_DESCONHECIDO,
    EstadoQR,
    QRCode,
    app,
    carregar_museu_json,
)

client = TestClient(app)


class TestEstadoQR(unittest.TestCase):
    def test_valores_compativeis_com_strings(self):
        esperado = {"pendente", "validado", "nulo", "vazio", "corrompido", "repetido"}
        self.assertEqual({estado.value for estado in EstadoQR}, esperado)
        self.assertEqual(EstadoQR.VALIDADO, "validado")

    def test_validar_devolve_o_estado_certo(self):
        casos = [
            ("MNSR-QR-01", EstadoQR.VALIDADO),
            (None, EstadoQR.NULO),
            ("", EstadoQR.VAZIO),
            ("   ", EstadoQR.VAZIO),
            ("XXXX", EstadoQR.CORROMPIDO),
            ("MNSR-QR-99", EstadoQR.CORROMPIDO),
            (123, EstadoQR.CORROMPIDO),
            (["MNSR-QR-01"], EstadoQR.CORROMPIDO),
        ]
        for codigo, esperado in casos:
            with self.subTest(codigo=codigo):
                qr = QRCode(codigo)
                qr.validar()
                self.assertIs(qr.estado, esperado)

    def test_estado_inicial_e_repetido_usam_o_enum(self):
        qr = QRCode("MNSR-QR-02")
        self.assertIs(qr.estado, EstadoQR.PENDENTE)
        qr.validar()
        qr.validar()
        self.assertIs(qr.estado, EstadoQR.REPETIDO)


class TestConstantes(unittest.TestCase):
    def test_autor_desconhecido_existe_no_acervo(self):
        autores = {obra.autor for obra in carregar_museu_json()}
        self.assertIn(AUTOR_DESCONHECIDO, autores)


class TestPistasEficiencia(unittest.TestCase):
    def test_pistas_le_o_acervo_uma_unica_vez(self):
        sessao = "teste-refactor"
        for codigo in ("MNSR-QR-01", "MNSR-QR-02", "MNSR-QR-03"):
            client.post("/qr/validar", json={"codigo": codigo, "sessao": sessao})
        with patch(
            "src.main.carregar_museu_json", wraps=carregar_museu_json
        ) as leitura:
            dados = client.get("/pistas", params={"sessao": sessao}).json()
        self.assertEqual(dados["desbloqueadas"], 3)
        self.assertEqual(leitura.call_count, 1)


if __name__ == "__main__":
    unittest.main()