#!/usr/bin/env python3
"""Teste de fumaça: gera um vídeo sintético e renderiza com o motor para conferir que tudo funciona.

Uso:  rodar.py teste
Não precisa de internet nem de nenhum vídeo seu. Leva ~1 minuto.
"""
import copy
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lib_common as lc

AQUI = Path(__file__).resolve().parent


def main():
    lc.garantir_ffmpeg()
    tmp = Path(tempfile.mkdtemp(prefix="editor-video-teste-"))
    video = tmp / "entrada.mp4"
    lc.rodar(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc2=size=720x1280:rate=30:duration=9",
              "-f", "lavfi", "-i", "sine=frequency=220:duration=9", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", str(video)])
    palavras = "Quer usar inteligência artificial para ganhar tempo no seu negócio hoje mesmo".split()
    words = [{"w": w + ("," if i == 5 else ""), "s": round(0.4 + i * 0.5, 2), "e": round(0.4 + i * 0.5 + 0.4, 2)} for i, w in enumerate(palavras)]
    analise = tmp / "saida" / "analise"
    lc.salvar_json(analise / "transcricao.json", [{"start": 0.4, "end": 5.5, "text": " ".join(palavras), "words": words}])
    marca = lc.ler_json(lc.SKILL_DIR / "templates" / "marca.exemplo.json")
    plano = {"titulo": "teste", "formato": "9:16", "cortes": [[0.0, 4.0], [4.5, 9.0]],
             "zoom": {"punches": [{"t": 2.0}, {"t": 6.0}]},
             "cards": [{"tipo": "titulo", "t0": 1.0, "t1": 3.5, "rotulo": "TESTE", "titulo": [["IA ", True], ["NO NEGÓCIO", False]], "sub": "sub"},
                       {"tipo": "lista", "t0": 5.0, "t1": 8.5, "rotulo": "LISTA", "itens": [["Um", 5.3], ["Dois", 6.2], ["Três", 7.1]]}],
             "sfx": [{"t": 1.0, "som": "pop-sintetico", "pico_db": -14}, {"t": 2.0, "som": "whoosh-sintetico", "pico_db": -14}]}
    lc.salvar_json(tmp / "marca.json", marca)
    lc.salvar_json(tmp / "plano.json", plano)
    # 1) o validador precisa aceitar o plano bom e recusar um botão de CTA
    ruim = copy.deepcopy(plano)
    ruim["cards"][0]["titulo"] = [["CLIQUE AQUI", False]]
    lc.salvar_json(tmp / "plano_ruim.json", ruim)
    r_ok = subprocess.call([sys.executable, str(AQUI / "validar.py"), "--marca", str(tmp / "marca.json"), "--plano", str(tmp / "plano.json"), "--projeto", str(tmp)])
    r_ruim = subprocess.call([sys.executable, str(AQUI / "validar.py"), "--marca", str(tmp / "marca.json"), "--plano", str(tmp / "plano_ruim.json"), "--projeto", str(tmp)],
                             stdout=subprocess.DEVNULL)
    assert r_ok == 0, "o plano bom foi recusado"
    assert r_ruim != 0, "o validador deveria recusar botão de CTA na tela"
    # 2) render
    subprocess.check_call([sys.executable, str(AQUI / "renderizar.py"), "--video", str(video), "--analise", str(analise), "--plano", str(tmp / "plano.json"),
                           "--marca", str(tmp / "marca.json"), "--saida", str(tmp / "saida"), "--projeto", str(tmp), "--prontos", str(tmp / "prontos"), "--preview"])
    saida = tmp / "prontos" / "teste_v1.mp4"
    assert saida.exists(), "o vídeo final não foi criado"
    info = lc.sondar_video(saida)
    assert (info["largura"], info["altura"]) == (1080, 1920), info
    assert info["tem_audio"], "o vídeo final está sem áudio"
    assert abs(info["duracao"] - 8.5) < 0.3, f"duração inesperada: {info['duracao']}"
    print(f"\nTESTE OK  ({info['duracao']:.1f}s, {info['largura']}x{info['altura']}). Arquivos em {tmp}")


if __name__ == "__main__":
    main()
