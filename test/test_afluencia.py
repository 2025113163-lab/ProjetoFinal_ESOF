import unittest

from src.afluencia import AfluenciaSala, NotificadorApp, ObservadorAfluencia


class ObservadorEspiao(ObservadorAfluencia):
    def __init__(self):
        self.chamadas: list[tuple[str, int, bool]] = []

    def atualizar(self, afluencia: AfluenciaSala) -> None:
        self.chamadas.append(
            (afluencia.sala, afluencia.visitantes_atuais, afluencia.lotada)
        )


class TestAfluenciaSala(unittest.TestCase):
    def setUp(self):
        self.sala = AfluenciaSala("Sala de Escultura", limite_maximo=3)
        self.espiao = ObservadorEspiao()
        self.sala.adicionar_observador(self.espiao)

    def test_limite_invalido(self):
        for limite in (0, -1):
            with self.assertRaises(ValueError):
                AfluenciaSala("Sala X", limite)

    def test_contagem_entradas_e_saidas(self):
        self.sala.registar_entrada()
        self.sala.registar_entrada()
        self.sala.registar_saida()
        self.assertEqual(self.sala.visitantes_atuais, 1)

    def test_saida_com_sala_vazia_nao_fica_negativa(self):
        self.sala.registar_saida()
        self.assertEqual(self.sala.visitantes_atuais, 0)
        self.assertEqual(self.espiao.chamadas, [])

    def test_abaixo_do_limite_nao_notifica(self):
        self.sala.registar_entrada()
        self.sala.registar_entrada()
        self.assertFalse(self.sala.lotada)
        self.assertEqual(self.espiao.chamadas, [])

    def test_notifica_ao_atingir_limite(self):
        for _ in range(3):
            self.sala.registar_entrada()
        self.assertTrue(self.sala.lotada)
        self.assertEqual(self.espiao.chamadas, [("Sala de Escultura", 3, True)])

    def test_nao_repete_notificacao_acima_do_limite(self):
        for _ in range(5):
            self.sala.registar_entrada()
        self.assertEqual(len(self.espiao.chamadas), 1)

    def test_notifica_ao_baixar_do_limite(self):
        for _ in range(3):
            self.sala.registar_entrada()
        self.sala.registar_saida()
        self.assertFalse(self.sala.lotada)
        self.assertEqual(self.espiao.chamadas[-1], ("Sala de Escultura", 2, False))
        self.assertEqual(len(self.espiao.chamadas), 2)

    def test_varios_observadores(self):
        outro = ObservadorEspiao()
        self.sala.adicionar_observador(outro)
        for _ in range(3):
            self.sala.registar_entrada()
        self.assertEqual(len(self.espiao.chamadas), 1)
        self.assertEqual(len(outro.chamadas), 1)

    def test_observador_duplicado_so_regista_uma_vez(self):
        self.sala.adicionar_observador(self.espiao)
        for _ in range(3):
            self.sala.registar_entrada()
        self.assertEqual(len(self.espiao.chamadas), 1)

    def test_remover_observador(self):
        self.sala.remover_observador(self.espiao)
        self.sala.remover_observador(self.espiao)  # remover 2x não falha
        for _ in range(3):
            self.sala.registar_entrada()
        self.assertEqual(self.espiao.chamadas, [])


class TestNotificadorApp(unittest.TestCase):
    def test_mensagens_de_sala_cheia_e_com_espaco(self):
        sala = AfluenciaSala("Sala de Pintura", limite_maximo=1)
        notificador = NotificadorApp()
        sala.adicionar_observador(notificador)
        sala.registar_entrada()
        sala.registar_saida()
        self.assertEqual(len(notificador.mensagens), 2)
        self.assertIn("cheia", notificador.mensagens[0])
        self.assertIn("Sala de Pintura", notificador.mensagens[0])
        self.assertIn("espaço", notificador.mensagens[1])


if __name__ == "__main__":
    unittest.main()
