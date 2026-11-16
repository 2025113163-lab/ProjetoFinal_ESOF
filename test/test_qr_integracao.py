import unittest

from fastapi.testclient import TestClient

from src.main import (
    _SESSOES,
    DesafioBeacon,
    DesafioFactory,
    DesafioPergunta,
    DesafioQR,
    QRCode,
    Recompensa,
    app,
    carregar_museu_json,
)

client = TestClient(app)


def _qr_validado(codigo: str) -> QRCode:
    qr = QRCode(codigo)
    qr.validar()
    return qr


def _resolver(n: int, sessao: str = "anonima") -> None:
    """Valida e resolve (via API) os desafios das primeiras n obras."""
    for obra in carregar_museu_json()[:n]:
        client.post("/qr/validar", json={"codigo": obra.codigo_qr, "sessao": sessao})
        resposta = obra.sala if obra.autor == "Desconhecido" else obra.autor
        client.post(
            "/desafios/responder",
            json={"codigo": obra.codigo_qr, "resposta": resposta, "sessao": sessao},
        )


class TestRecompensa(unittest.TestCase):
    def test_sem_medalha_abaixo_de_tres(self):
        for n in (0, 1, 2, -5):
            with self.subTest(n=n):
                r = Recompensa(n)
                self.assertIsNone(r.medalha)
                self.assertEqual(r.desconto, 0)

    def test_niveis_de_medalha_e_desconto(self):
        esperado = {
            3: ("Bronze", 5),
            5: ("Bronze", 5),
            6: ("Prata", 10),
            9: ("Prata", 10),
            10: ("Ouro", 15),
            15: ("Ouro", 15),
        }
        for n, (medalha, desconto) in esperado.items():
            with self.subTest(n=n):
                r = Recompensa(n)
                self.assertEqual(r.medalha, medalha)
                self.assertEqual(r.desconto, desconto)

    def test_como_dict(self):
        self.assertEqual(
            Recompensa(4).como_dict(),
            {"resolvidas": 4, "medalha": "Bronze", "desconto_percentagem": 5},
        )


class TestTiposDesafio(unittest.TestCase):
    def test_tipos_disponiveis(self):
        self.assertEqual(DesafioFactory.TIPOS, ("pergunta", "qr", "beacon"))

    def test_factory_devolve_a_classe_certa(self):
        esperado = {
            "pergunta": DesafioPergunta,
            "qr": DesafioQR,
            "beacon": DesafioBeacon,
        }
        for tipo, classe in esperado.items():
            with self.subTest(tipo=tipo):
                desafio = DesafioFactory().criarDesafio(_qr_validado("MNSR-QR-01"), tipo)
                self.assertIsInstance(desafio, classe)
                self.assertEqual(desafio.tipo, tipo)
                self.assertFalse(desafio.resolvido)

    def test_tipo_por_defeito_e_pergunta(self):
        desafio = DesafioFactory().criarDesafio(_qr_validado("MNSR-QR-01"))
        self.assertEqual(desafio.tipo, "pergunta")

    def test_desafio_qr_aponta_para_obra_seguinte(self):
        desafio = DesafioFactory().criarDesafio(_qr_validado("MNSR-QR-01"), "qr")
        self.assertIn("Autorretrato", desafio.pergunta)
        self.assertTrue(desafio.verificarResposta("mnsr-qr-02"))
        self.assertTrue(desafio.resolvido)

    def test_desafio_qr_da_a_volta_ao_acervo(self):
        desafio = DesafioFactory().criarDesafio(_qr_validado("MNSR-QR-15"), "qr")
        self.assertTrue(desafio.verificarResposta("MNSR-QR-01"))

    def test_desafio_beacon_simulado(self):
        desafio = DesafioFactory().criarDesafio(_qr_validado("MNSR-QR-01"), "beacon")
        self.assertIn("beacon", desafio.pergunta.lower())
        self.assertFalse(desafio.verificarResposta("MNSR-QR-01"))
        self.assertTrue(desafio.verificarResposta("MNSR-BCN-01"))

    def test_tipo_desconhecido_levanta_erro(self):
        with self.assertRaises(ValueError):
            DesafioFactory().criarDesafio(_qr_validado("MNSR-QR-01"), "hologram")


class TestIntegracaoQRePistas(unittest.TestCase):
    def setUp(self):
        _SESSOES.clear()

    def test_validar_com_tipo_qr(self):
        r = client.post("/qr/validar", json={"codigo": "MNSR-QR-01", "tipo": "qr"})
        self.assertEqual(r.status_code, 200)
        desafio = r.json()["desafio"]
        self.assertEqual(desafio["tipo"], "qr")
        self.assertIn("Autorretrato", desafio["pergunta"])

    def test_tipo_invalido_nao_consome_o_qr(self):
        r = client.post("/qr/validar", json={"codigo": "MNSR-QR-01", "tipo": "xpto"})
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.json()["detail"]["estado"], "tipo_invalido")
        self.assertEqual(client.get("/pistas").json()["desbloqueadas"], 0)
        # o mesmo QR continua a poder ser validado
        r = client.post("/qr/validar", json={"codigo": "MNSR-QR-01"})
        self.assertEqual(r.status_code, 200)

    def test_codigo_em_lista_e_corrompido(self):
        r = client.post("/qr/validar", json={"codigo": ["MNSR-QR-01"]})
        self.assertEqual(r.status_code, 422)
        self.assertEqual(r.json()["detail"]["estado"], "corrompido")

    def test_responder_certo(self):
        client.post("/qr/validar", json={"codigo": "MNSR-QR-01"})
        r = client.post(
            "/desafios/responder",
            json={"codigo": "MNSR-QR-01", "resposta": "antonio soares dos reis"},
        )
        self.assertEqual(r.status_code, 200)
        dados = r.json()
        self.assertTrue(dados["correta"])
        self.assertTrue(dados["resolvido"])
        self.assertEqual(dados["recompensa"]["resolvidas"], 1)
        self.assertIsNone(dados["recompensa"]["medalha"])

    def test_responder_errado_ou_nulo(self):
        client.post("/qr/validar", json={"codigo": "MNSR-QR-01"})
        for resposta in ("Aurélia de Souza", None):
            r = client.post(
                "/desafios/responder",
                json={"codigo": "MNSR-QR-01", "resposta": resposta},
            )
            self.assertEqual(r.status_code, 200)
            self.assertFalse(r.json()["correta"])
            self.assertFalse(r.json()["resolvido"])

    def test_responder_sem_desbloquear_da_404(self):
        r = client.post(
            "/desafios/responder", json={"codigo": "MNSR-QR-01", "resposta": "x"}
        )
        self.assertEqual(r.status_code, 404)
        self.assertEqual(r.json()["detail"]["estado"], "nao_desbloqueado")

    def test_resolver_duas_vezes_conta_uma_vez(self):
        _resolver(1)
        _resolver(1)  # 2.ª validação -> 409; 2.ª resposta correta
        dados = client.get("/pistas").json()
        self.assertEqual(dados["recompensa"]["resolvidas"], 1)

    def test_pistas_mostra_tipo_e_resolvido(self):
        _resolver(1)
        pista = client.get("/pistas").json()["pistas"][0]
        self.assertEqual(pista["tipo"], "pergunta")
        self.assertTrue(pista["resolvido"])

    def test_medalhas_e_descontos_em_pistas(self):
        esperado = {3: ("Bronze", 5), 6: ("Prata", 10), 10: ("Ouro", 15)}
        for n, (medalha, desconto) in esperado.items():
            with self.subTest(n=n):
                _SESSOES.clear()
                _resolver(n)
                recompensa = client.get("/pistas").json()["recompensa"]
                self.assertEqual(recompensa["resolvidas"], n)
                self.assertEqual(recompensa["medalha"], medalha)
                self.assertEqual(recompensa["desconto_percentagem"], desconto)

    def test_desbloquear_sem_resolver_nao_da_medalha(self):
        for obra in carregar_museu_json()[:5]:
            client.post("/qr/validar", json={"codigo": obra.codigo_qr})
        dados = client.get("/pistas").json()
        self.assertEqual(dados["desbloqueadas"], 5)
        self.assertIsNone(dados["recompensa"]["medalha"])

    def test_recompensas_isoladas_por_sessao(self):
        _resolver(3, sessao="a")
        dados = client.get("/pistas", params={"sessao": "b"}).json()
        self.assertEqual(dados["recompensa"]["resolvidas"], 0)
        self.assertIsNone(dados["recompensa"]["medalha"])


if __name__ == "__main__":
    unittest.main()