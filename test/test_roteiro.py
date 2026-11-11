import unittest
from fastapi.testclient import TestClient
from src.main import (
    app,
    carregar_museu_json,
    gerador_roteiro,
    RotaMaisCurta,
    RotaMenosCrowded,
    RotaFamiliar,
)

client = TestClient(app)


class TestRoteiro(unittest.TestCase):
    def setUp(self):
        self.obras = carregar_museu_json("data/museu.json")

    def test_tempo_e_interesse_escultura(self):
        """US-01: Roteiro respeita o tempo limite e filtra pelo interesse."""
        tempo_max = 60
        interesse = "Escultura"

        roteiro = gerador_roteiro(self.obras, tempo_max, interesse)
        tempo_total = roteiro.calcular_tempo_total()

        self.assertGreater(len(roteiro.obras), 0)
        self.assertLessEqual(tempo_total, tempo_max)
        for obra in roteiro.obras:
            self.assertTrue(
                interesse.lower() in obra.tema.lower()
                or interesse.lower() in obra.sala.lower()
            )

    def test_tempo_curto_limite(self):
        """US-01: Tempo de 12 minutos só permite incluir obras até 12 min."""
        roteiro = gerador_roteiro(self.obras, 12, "Escultura")
        self.assertLessEqual(roteiro.calcular_tempo_total(), 12)

    def test_interesse_inexistente_devolve_vazio(self):
        """US-01: Interesse sem obras devolve roteiro com tempo 0."""
        roteiro = gerador_roteiro(self.obras, 60, "Astronomia")
        self.assertEqual(len(roteiro.obras), 0)
        self.assertEqual(roteiro.calcular_tempo_total(), 0)

    def test_estrategias_roteiro(self):
        """US-01 / Padrão Strategy: Testa RotaMaisCurta, RotaMenosCrowded e RotaFamiliar."""
        r_curta = gerador_roteiro(self.obras, 30, strategy=RotaMaisCurta())
        r_crowded = gerador_roteiro(self.obras, 30, strategy=RotaMenosCrowded())
        r_familiar = gerador_roteiro(self.obras, 30, strategy=RotaFamiliar())

        self.assertLessEqual(r_curta.calcular_tempo_total(), 30)
        self.assertLessEqual(r_crowded.calcular_tempo_total(), 30)
        self.assertLessEqual(r_familiar.calcular_tempo_total(), 30)
        for obra in r_familiar.obras:
            self.assertLessEqual(obra.minutos_visita, 8)

    def test_endpoint_roteiros(self):
        """Testa o endpoint GET /roteiros."""
        response = client.get("/roteiros?tempo=30&interesse=Escultura&estrategia=curta")
        self.assertEqual(response.status_code, 200)
        dados = response.json()
        self.assertLessEqual(dados["tempo_total"], 30)
        self.assertGreater(len(dados["obras"]), 0)


if __name__ == "__main__":
    unittest.main()