import unittest

from fastapi.testclient import TestClient
from src.main import _SESSOES, Desafio, DesafioFactory, QRCode, app

client = TestClient(app)


class TestQRCode(unittest.TestCase):
    def test_estado_inicial_pendente(self):
        self.assertEqual(QRCode("MNSR-QR-01").estado, "pendente")

    def test_qr_valido(self):
        qr = QRCode("MNSR-QR-01")
        self.assertTrue(qr.validar())
        self.assertEqual(qr.estado, "validado")

    def test_qr_nulo(self):
        qr = QRCode(None)
        self.assertFalse(qr.validar())
        self.assertEqual(qr.estado, "nulo")

    def test_qr_vazio(self):
        for codigo in ("", "   "):
            qr = QRCode(codigo)
            self.assertFalse(qr.validar())
            self.assertEqual(qr.estado, "vazio")

    def test_qr_corrompido(self):
        # formato errado, código inexistente, espaço extra e tipo inválido
        for codigo in ("XXXX", "MNSR-QR-99", "MNSR-QR-01 ", 12345):
            qr = QRCode(codigo)
            self.assertFalse(qr.validar())
            self.assertEqual(qr.estado, "corrompido")

    def test_qr_repetido(self):
        qr = QRCode("MNSR-QR-02")
        self.assertTrue(qr.validar())
        self.assertFalse(qr.validar())
        self.assertEqual(qr.estado, "repetido")
        self.assertFalse(qr.validar())
        self.assertEqual(qr.estado, "repetido")


class TestDesafioFactory(unittest.TestCase):
    def test_criar_desafio_com_autor(self):
        qr = QRCode("MNSR-QR-01")
        qr.validar()
        desafio = DesafioFactory().criarDesafio(qr)
        self.assertIsInstance(desafio, Desafio)
        self.assertIn("O Desterrado", desafio.pergunta)
        self.assertFalse(desafio.resolvido)

    def test_resposta_correta_ignora_acentos_e_maiusculas(self):
        qr = QRCode("MNSR-QR-01")
        qr.validar()
        desafio = DesafioFactory().criarDesafio(qr)
        self.assertTrue(desafio.verificarResposta("  antonio SOARES dos reis "))
        self.assertTrue(desafio.resolvido)

    def test_resposta_errada_ou_invalida(self):
        qr = QRCode("MNSR-QR-01")
        qr.validar()
        desafio = DesafioFactory().criarDesafio(qr)
        self.assertFalse(desafio.verificarResposta("Aurélia de Souza"))
        self.assertFalse(desafio.verificarResposta(None))
        self.assertFalse(desafio.resolvido)

    def test_autor_desconhecido_pergunta_pela_sala(self):
        qr = QRCode("MNSR-QR-03")
        qr.validar()
        desafio = DesafioFactory().criarDesafio(qr)
        self.assertIn("sala", desafio.pergunta.lower())
        self.assertTrue(desafio.verificarResposta("sala de ceramica"))

    def test_qr_nao_validado_levanta_erro(self):
        with self.assertRaises(ValueError):
            DesafioFactory().criarDesafio(QRCode("MNSR-QR-01"))
        qr = QRCode("MNSR-QR-99")
        qr.validar()
        with self.assertRaises(ValueError):
            DesafioFactory().criarDesafio(qr)


class TestEndpointsQR(unittest.TestCase):
    def setUp(self):
        _SESSOES.clear()

    def test_validar_qr_valido(self):
        r = client.post("/qr/validar", json={"codigo": "MNSR-QR-01"})
        self.assertEqual(r.status_code, 200)
        dados = r.json()
        self.assertTrue(dados["valido"])
        self.assertEqual(dados["estado"], "validado")
        self.assertEqual(dados["obra"]["titulo"], "O Desterrado")
        self.assertIn("O Desterrado", dados["desafio"]["pergunta"])
        self.assertFalse(dados["desafio"]["resolvido"])

    def test_validar_qr_nulo(self):
        for corpo in ({"codigo": None}, {}):
            r = client.post("/qr/validar", json=corpo)
            self.assertEqual(r.status_code, 400)
            self.assertEqual(r.json()["detail"]["estado"], "nulo")

    def test_validar_qr_vazio(self):
        r = client.post("/qr/validar", json={"codigo": "  "})
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.json()["detail"]["estado"], "vazio")

    def test_validar_qr_corrompido(self):
        for codigo in ("MNSR-QR-99", "lixo", 123):
            r = client.post("/qr/validar", json={"codigo": codigo})
            self.assertEqual(r.status_code, 422)
            self.assertEqual(r.json()["detail"]["estado"], "corrompido")

    def test_validar_qr_repetido(self):
        client.post("/qr/validar", json={"codigo": "MNSR-QR-05"})
        r = client.post("/qr/validar", json={"codigo": "MNSR-QR-05"})
        self.assertEqual(r.status_code, 409)
        self.assertEqual(r.json()["detail"]["estado"], "repetido")

    def test_sessoes_independentes(self):
        corpo_a = {"codigo": "MNSR-QR-01", "sessao": "visitante-a"}
        corpo_b = {"codigo": "MNSR-QR-01", "sessao": "visitante-b"}
        self.assertEqual(client.post("/qr/validar", json=corpo_a).status_code, 200)
        self.assertEqual(client.post("/qr/validar", json=corpo_b).status_code, 200)

    def test_pistas_vazias(self):
        r = client.get("/pistas")
        self.assertEqual(r.status_code, 200)
        dados = r.json()
        self.assertEqual(dados["desbloqueadas"], 0)
        self.assertEqual(dados["total_obras"], 15)
        self.assertEqual(dados["pistas"], [])

    def test_pistas_apos_validar(self):
        client.post("/qr/validar", json={"codigo": "MNSR-QR-01"})
        client.post("/qr/validar", json={"codigo": "MNSR-QR-03"})
        client.post("/qr/validar", json={"codigo": "MNSR-QR-99"})  # não conta
        dados = client.get("/pistas").json()
        self.assertEqual(dados["desbloqueadas"], 2)
        titulos = {p["titulo"] for p in dados["pistas"]}
        self.assertEqual(
            titulos, {"O Desterrado", "Pote (Dinastia Ming, período Jiajing)"}
        )

    def test_pistas_isoladas_por_sessao(self):
        client.post("/qr/validar", json={"codigo": "MNSR-QR-01", "sessao": "x"})
        dados = client.get("/pistas", params={"sessao": "y"}).json()
        self.assertEqual(dados["desbloqueadas"], 0)


if __name__ == "__main__":
    unittest.main()