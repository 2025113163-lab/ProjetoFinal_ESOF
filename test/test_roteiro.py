import unittest
from src.main import carregar_museu_json, gerador_roteiro

class TestRoteiro(unittest.TestCase):
    def setUp(self):
        self.obras = carregar_museu_json('data/museu.json')

    def test_tempo(self):
        tempo_max = 60
        interesse_esco = "Escultura"

        roteiro = gerador_roteiro(self.obras, tempo_max, interesse_esco)
        tempo_total = roteiro.calcular_tempo_total()
        self.assertLessEqual(tempo_total, tempo_max, f"Tempo total do roteiro ({tempo_total} minutos) excede o tempo máximo permitido ({tempo_max} minutos).")
        for obra in roteiro.obras:
            self.assertIn(interesse_esco, obra.autor, f"Obra '{obra.titulo}' não corresponde ao interesse especificado '{interesse_esco}'.")

if __name__ == '__main__':
    unittest.main()