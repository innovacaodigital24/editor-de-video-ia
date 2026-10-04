#!/usr/bin/env python3
"""Limpa efeitos sonoros: tira silêncio do início, limita a duração com fade e iguala o volume.

Uso:  rodar.py sfx-preparar --entrada PASTA_POR_CATEGORIA --saida PASTA/pronto
A pasta de entrada deve ter subpastas por categoria (click, pop, whoosh...).
Saída: arquivos 'categoria__nome.wav' em WAV 48 kHz estéreo.
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lib_common as lc

SR = 48000
# categoria: (duração máxima em s, fade de saída em s)
CFG = {"click": (0.35, 0.05), "mouse-click": (0.4, 0.05), "pop": (0.45, 0.08), "pop-whoosh": (0.4, 0.06),
       "bell": (1.6, 0.5), "whoosh": (0.9, 0.25), "impact": (1.6, 0.6), "riser": (2.4, 0.04),
       "snap": (0.3, 0.08), "camera": (0.5, 0.1), "success": (1.4, 0.4), "typing": (3.0, 0.3)}


def reamostrar(m, sr):
    if sr == SR:
        return m
    n = int(len(m) * SR / sr)
    return np.interp(np.linspace(0, len(m) - 1, n), np.arange(len(m)), m)


def finalizar(m, cat):
    mx, fo = CFG.get(cat, (1.5, 0.2))
    idx = np.where(np.abs(m) > 10 ** (-42 / 20))[0]
    m = m[max(0, idx[0] - int(0.003 * SR)):] if len(idx) else m
    if cat == "riser":
        pk = int(np.argmax(np.abs(m)))
        m = m[max(0, pk - int((mx - 0.25) * SR)):pk + int(0.25 * SR)]
    elif cat == "whoosh":
        k = int(0.05 * SR)
        env = np.convolve(np.abs(m), np.ones(k) / k, "same")
        pk = int(np.argmax(env))
        m = m[max(0, pk - int(mx * 0.55 * SR)):][:int(mx * SR)]
    else:
        m = m[:int(mx * SR)]
    m = m.copy()
    n = min(len(m), int(fo * SR))
    m[-n:] *= np.linspace(1, 0, n)
    fi = int(0.004 * SR)
    m[:fi] *= np.linspace(0, 1, fi)
    ativo = np.abs(m) > np.abs(m).max() * 0.05
    g = 10 ** (-22 / 20) / (np.sqrt(np.mean(m[ativo] ** 2)) + 1e-9)
    if np.abs(m).max() * g > 10 ** (-3 / 20):
        g = 10 ** (-3 / 20) / np.abs(m).max()
    return m * g


def preparar_arquivo(origem, cat, destino_dir):
    x, sr = sf.read(str(origem))
    m = x.mean(axis=1) if x.ndim > 1 else x
    o = finalizar(reamostrar(m, sr), cat)
    destino = Path(destino_dir) / f"{cat}__{Path(origem).stem}.wav"
    sf.write(str(destino), np.stack([o, o], 1), SR, subtype="PCM_16")
    return destino


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--entrada", required=True)
    ap.add_argument("--saida", default=str(lc.CONFIG_DIR / "sfx" / "pronto"))
    a = ap.parse_args()
    Path(a.saida).mkdir(parents=True, exist_ok=True)
    total = 0
    for cat_dir in sorted(p for p in Path(a.entrada).iterdir() if p.is_dir() and p.name in CFG):
        for f in sorted(cat_dir.glob("*.wav")):
            preparar_arquivo(f, cat_dir.name, a.saida)
            total += 1
    print(f"{total} efeitos preparados em {a.saida}")


if __name__ == "__main__":
    main()
