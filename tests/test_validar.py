"""Testes rápidos das regras do validador (só biblioteca padrão)."""
import copy
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "skills" / "editor-de-video-ia" / "scripts"))
import lib_common as lc  # noqa: E402
import validar  # noqa: E402

MARCA = lc.ler_json(RAIZ / "skills" / "editor-de-video-ia" / "templates" / "marca.exemplo.json")
PLANO = lc.ler_json(RAIZ / "skills" / "editor-de-video-ia" / "templates" / "plano.exemplo.json")


class TestMarca(unittest.TestCase):
    def test_marca_exemplo_e_valida(self):
        erros, _ = validar.validar_marca(MARCA)
        self.assertEqual(erros, [])

    def test_hex_invalido(self):
        m = copy.deepcopy(MARCA); m["cores"]["destaque"] = "verde"
        erros, _ = validar.validar_marca(m)
        self.assertTrue(any("destaque" in e for e in erros))

    def test_contraste_baixo_gera_aviso(self):
        m = copy.deepcopy(MARCA); m["cores"]["texto"] = "#222222"
        _, alertas = validar.validar_marca(m)
        self.assertTrue(alertas)

    def test_exemplos_do_repositorio_sao_validos(self):
        for arq in (RAIZ / "examples").glob("marca-*.json"):
            erros, _ = validar.validar_marca(lc.ler_json(arq))
            self.assertEqual(erros, [], arq.name)


class TestPlano(unittest.TestCase):
    def validar(self, plano, marca=MARCA):
        return validar.validar_plano(plano, marca, str(RAIZ))

    def test_plano_exemplo_e_valido(self):
        erros, _ = self.validar(PLANO)
        self.assertEqual(erros, [])

    def test_botao_cta_e_recusado(self):
        p = copy.deepcopy(PLANO); p["cards"][0]["titulo"] = [["SAIBA MAIS", False]]
        erros, _ = self.validar(p)
        self.assertTrue(any("CTA" in e for e in erros))

    def test_botao_cta_liberado_quando_a_marca_permite(self):
        m = copy.deepcopy(MARCA); m["regras"]["sem_botao_cta_na_tela"] = False
        p = copy.deepcopy(PLANO); p["cards"][0]["titulo"] = [["SAIBA MAIS", False]]
        erros, _ = self.validar(p, m)
        self.assertEqual(erros, [])

    def test_palavra_a_evitar_em_card(self):
        m = copy.deepcopy(MARCA); m["vocabulario"]["evitar"] = ["garantido"]
        p = copy.deepcopy(PLANO); p["cards"][1]["itens"][0][0] = "Resultado garantido"
        erros, _ = self.validar(p, m)
        self.assertTrue(any("garantido" in e for e in erros))

    def test_cards_sobrepostos(self):
        p = copy.deepcopy(PLANO); p["cards"][1]["t0"] = 5.0
        erros, _ = self.validar(p)
        self.assertTrue(any("sobrep" in e for e in erros))

    def test_cortes_fora_de_ordem(self):
        p = copy.deepcopy(PLANO); p["cortes"] = [[10, 20], [5, 8]]
        erros, _ = self.validar(p)
        self.assertTrue(erros)

    def test_arquivo_de_midia_inexistente(self):
        p = copy.deepcopy(PLANO); p["inserts"] = [{"arquivo": "nao/existe.png", "t0": 1, "t1": 2}]
        erros, _ = self.validar(p)
        self.assertTrue(any("não encontrado" in e for e in erros))


if __name__ == "__main__":
    unittest.main()
