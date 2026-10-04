#!/usr/bin/env python3
"""Gera efeitos sonoros sintéticos (whoosh, pop, impacto, riser, click, snap).

São criados no seu computador com matemática pura, então não têm licença de
terceiros e podem ser usados e distribuídos livremente. Servem de base e de
reserva quando você ainda não baixou uma biblioteca de sons.
"""
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy import signal

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lib_common as lc
from sfx_preparar import SR, finalizar

rng = np.random.default_rng(7)


def whoosh(d=0.35, reverso=False):
    n = int(d * SR)
    ruido = rng.standard_normal(n)
    saida = np.zeros(n)
    bloco = int(0.005 * SR)
    for i in range(0, n, bloco):
        fc = 200 * (6000 / 200) ** (i / n)
        sos = signal.butter(2, [fc * 0.7, min(fc * 1.4, SR / 2 - 100)], btype="band", fs=SR, output="sos")
        saida[i:i + bloco] = signal.sosfilt(sos, ruido[i:i + bloco])
    t = np.linspace(0, 1, n)
    o = saida * np.where(t < 0.7, (t / 0.7) ** 2, np.exp(-(t - 0.7) * 14))
    return o[::-1] if reverso else o


def pop():
    n = int(0.08 * SR); t = np.arange(n) / SR
    f = 700 + 400 * np.exp(-t * 60)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.02)


def click():
    n = int(0.05 * SR); t = np.arange(n) / SR
    return (rng.standard_normal(n) * np.exp(-t / 0.004)) + np.sin(2 * np.pi * 2200 * t) * np.exp(-t / 0.01)


def snap():
    n = int(0.2 * SR); t = np.arange(n) / SR
    b = signal.butter(2, [1500, 9000], "band", fs=SR, output="sos")
    return signal.sosfilt(b, rng.standard_normal(n)) * np.exp(-t / 0.025)


def impacto():
    n = int(0.9 * SR); t = np.arange(n) / SR
    f = 40 + 50 * np.exp(-t * 12)
    corpo = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.25)
    grave = signal.sosfilt(signal.butter(2, 300, "low", fs=SR, output="sos"), rng.standard_normal(n)) * np.exp(-t / 0.08) * 0.6
    return corpo + grave


def riser():
    n = int(2.0 * SR); t = np.linspace(0, 1, n)
    f = 120 * (3000 / 120) ** t
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * t ** 2 + rng.standard_normal(n) * 0.05 * t ** 3


def sino():
    n = int(1.4 * SR); t = np.arange(n) / SR
    return sum(np.sin(2 * np.pi * f * t) * np.exp(-t / d) for f, d in ((880, 0.5), (1320, 0.35), (2200, 0.2)))


SONS = [("pop", "pop-sintetico", pop()), ("click", "click-sintetico", click()), ("snap", "snap-sintetico", snap()),
        ("whoosh", "whoosh-sintetico", whoosh()), ("whoosh", "whoosh-reverso-sintetico", whoosh(0.3, True)),
        ("impact", "impact-sintetico", impacto()), ("riser", "riser-sintetico", riser()), ("bell", "bell-sintetico", sino())]


def main():
    destino = lc.CONFIG_DIR / "sfx" / "pronto"
    destino.mkdir(parents=True, exist_ok=True)
    for cat, nome, som in SONS:
        o = finalizar(som, cat)
        sf.write(str(destino / f"{cat}__{nome}.wav"), np.stack([o, o], 1), SR, subtype="PCM_16")
    print(f"{len(SONS)} efeitos sintéticos em {destino}")


if __name__ == "__main__":
    main()
