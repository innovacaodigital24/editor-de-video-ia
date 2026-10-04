#!/usr/bin/env python3
"""Baixa uma biblioteca de efeitos sonoros livres (Mixkit + Wikimedia) para o SEU computador.

Os arquivos de som não fazem parte deste repositório: a licença do Mixkit permite
uso comercial, mas proíbe redistribuir os arquivos soltos. Por isso cada pessoa
baixa os seus, direto da fonte, e este script organiza e limpa tudo.

Uso:  rodar.py sfx-baixar --sim        (aceita a licença e baixa)
"""
import argparse
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lib_common as lc
from sfx_preparar import SR, preparar_arquivo


def baixar(url, destino):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 editor-de-video-ia"})
    with urllib.request.urlopen(req, timeout=60) as r, open(destino, "wb") as f:
        f.write(r.read())


def cortar_estalos(wav, pasta, quantidade=4):
    x, sr = sf.read(str(wav))
    m = x.mean(axis=1) if x.ndim > 1 else x
    hop = int(0.005 * sr)
    env = np.array([np.abs(m[i:i + hop]).max() for i in range(0, len(m) - hop, hop)])
    limiar, inicios, ultimo = env.max() * 0.35, [], -99
    for i, v in enumerate(env):
        if v > limiar and i - ultimo > 40:
            inicios.append(i * hop); ultimo = i
    melhores = sorted(sorted(inicios, key=lambda o: -np.abs(m[o:o + int(0.3 * sr)]).max())[:quantidade])
    pasta.mkdir(parents=True, exist_ok=True)
    for k, o in enumerate(melhores, 1):
        seg = m[max(0, o - int(0.01 * sr)):][:int(0.35 * sr)]
        sf.write(str(pasta / f"finger-snap-{k}.wav"), seg / (np.abs(seg).max() + 1e-9) * 0.9, sr, subtype="PCM_16")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sim", action="store_true", help="aceito as licenças das fontes e quero baixar")
    a = ap.parse_args()
    cat = lc.ler_json(lc.SKILL_DIR / "templates" / "sfx_catalogo.json")
    mk = cat["mixkit"]
    print(cat["aviso"], "\n")
    print(f"Mixkit: {mk['licenca']} ({mk['licenca_url']})\n  {mk['resumo']}")
    print(f"Wikimedia: {cat['wikimedia']['arquivo']} ({cat['wikimedia']['licenca']})\n")
    if not a.sim:
        sys.exit("Para baixar, rode de novo com --sim (confirma que você leu e aceita as licenças).")
    lc.garantir_ffmpeg()
    base = lc.CONFIG_DIR / "sfx"
    orig = base / "originais"
    ok = 0
    for s in mk["sons"]:
        pasta = orig / s["categoria"]
        pasta.mkdir(parents=True, exist_ok=True)
        mp3, wav = pasta / f"{s['nome']}.mp3", pasta / f"{s['nome']}.wav"
        try:
            if not wav.exists():
                baixar(mk["url_modelo"].format(id=s["id"]), mp3)
                lc.rodar(["ffmpeg", "-v", "error", "-y", "-i", str(mp3), "-ar", str(SR), "-ac", "2", str(wav)])
                mp3.unlink()
            ok += 1
            time.sleep(0.4)  # educado com o servidor
        except Exception as e:
            print(f"  falhou {s['nome']}: {e}")
    try:
        w = cat["wikimedia"]
        tmp = orig / "snap" / "finger_clicks.ogg"
        (orig / "snap").mkdir(parents=True, exist_ok=True)
        baixar(w["url"], tmp)
        lc.rodar(["ffmpeg", "-v", "error", "-y", "-i", str(tmp), "-ar", str(SR), "-ac", "2", str(orig / "snap" / "bruto.wav")])
        cortar_estalos(orig / "snap" / "bruto.wav", orig / "snap")
        (orig / "snap" / "bruto.wav").unlink()
    except Exception as e:
        print(f"  estalo de dedos não baixado: {e}")
    pronto = base / "pronto"
    pronto.mkdir(parents=True, exist_ok=True)
    total = 0
    for cat_dir in sorted(p for p in orig.iterdir() if p.is_dir()):
        for f in sorted(cat_dir.glob("*.wav")):
            preparar_arquivo(f, cat_dir.name, pronto); total += 1
    print(f"\n{ok} sons do Mixkit baixados. {total} efeitos prontos em {pronto}")


if __name__ == "__main__":
    main()
