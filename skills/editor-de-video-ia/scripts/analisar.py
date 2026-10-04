#!/usr/bin/env python3
"""Analisa um vídeo: dados técnicos, transcrição com tempo por palavra, silêncios, cenas e cortes sugeridos.

Uso:  rodar.py analisar VIDEO [--saida PASTA] [--modelo small] [--idioma pt] [--silencio-db -35]
Gera em PASTA/analise/: audio16k.wav, transcricao.json, silencios.json, cenas.json, resumo.json
"""
import argparse
import json
import re
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lib_common as lc

FPS = 30


def extrair_audio(video, destino):
    lc.rodar(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-vn", "-ac", "1", "-ar", "16000", str(destino)])


def detectar_silencios(video, db, minimo):
    r = lc.rodar(["ffmpeg", "-i", str(video), "-af", f"silencedetect=noise={db}dB:d={minimo}", "-f", "null", "-"],
                 check=False, capturar=True)
    ini = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", r.stderr)]
    fim = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r.stderr)]
    return [{"inicio": a, "fim": b, "duracao": round(b - a, 3)} for a, b in zip(ini, fim)]


def detectar_cenas(video):
    try:
        from scenedetect import ContentDetector, detect
        cenas = detect(str(video), ContentDetector(threshold=22, min_scene_len=8))
        return [round(c[0].get_seconds(), 2) for c in cenas[1:]]
    except Exception as e:
        print(f"  aviso: detecção de cenas indisponível ({e})")
        return []


def inicio_real(audio, sr, t0, t1, limiar_db=-38):
    """O Whisper costuma marcar a primeira palavra depois de uma pausa cedo demais.
    Procura o primeiro ponto com energia real."""
    t = t0
    while t < t1:
        s = audio[int(t * sr):int((t + 0.01) * sr)]
        if len(s) and 20 * np.log10(np.sqrt(np.mean(s ** 2)) + 1e-9) > limiar_db:
            return t
        t += 0.01
    return t0


def transcrever(audio_wav, modelo, idioma):
    from faster_whisper import WhisperModel
    print(f"  transcrevendo com o modelo '{modelo}' (na primeira vez baixa o modelo, é normal demorar)")
    m = WhisperModel(modelo, device="cpu", compute_type="int8")
    segs, info = m.transcribe(str(audio_wav), language=idioma, word_timestamps=True, vad_filter=False)
    x, sr = sf.read(str(audio_wav))
    saida = []
    for s in segs:
        palavras = []
        for i, w in enumerate(s.words):
            ini, fim = w.start, w.end
            if i == 0:
                ini = min(max(ini, inicio_real(x, sr, ini, fim)), fim - 0.05)
            palavras.append({"w": w.word.strip(), "s": round(ini, 3), "e": round(fim, 3)})
        saida.append({"start": round(s.start, 3), "end": round(s.end, 3), "text": s.text.strip(), "words": palavras})
    return saida


def sugerir_cortes(duracao, silencios, modo):
    """Mantém a fala e encurta pausas. modo: 'agressivo' (deixa 0.08s) ou 'suave' (deixa 0.2s)."""
    if modo == "nenhum" or not silencios:
        return [[0.0, round(duracao, 3)]]
    sobra = 0.08 if modo == "agressivo" else 0.20
    cortes, cursor = [], 0.0
    for s in silencios:
        ini_corte = s["inicio"] + sobra
        fim_corte = s["fim"] - sobra
        if fim_corte - ini_corte < 0.18:
            continue
        a, b = round(round(ini_corte * FPS) / FPS, 3), round(round(fim_corte * FPS) / FPS, 3)
        if a > cursor + 0.2:
            cortes.append([round(cursor, 3), a])
        cursor = b
    cortes.append([round(cursor, 3), round(duracao, 3)])
    return cortes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--saida", default="saida")
    ap.add_argument("--modelo", default="small", help="tiny, base, small ou medium")
    ap.add_argument("--idioma", default="pt")
    ap.add_argument("--silencio-db", type=float, default=-35)
    ap.add_argument("--silencio-min", type=float, default=0.4)
    ap.add_argument("--modo-cortes", default="suave", choices=["suave", "agressivo", "nenhum"])
    a = ap.parse_args()
    lc.garantir_ffmpeg()
    video = Path(a.video)
    if not video.exists():
        sys.exit(f"Vídeo não encontrado: {video}")
    pasta = Path(a.saida) / "analise"
    pasta.mkdir(parents=True, exist_ok=True)
    info = lc.sondar_video(video)
    print("1/4 Dados técnicos:", info)
    wav = pasta / "audio16k.wav"
    extrair_audio(video, wav)
    print("2/4 Procurando silêncios")
    sil = detectar_silencios(video, a.silencio_db, a.silencio_min)
    print("3/4 Procurando cenas")
    cenas = detectar_cenas(video)
    print("4/4 Transcrevendo")
    trans = transcrever(wav, a.modelo, a.idioma) if info["tem_audio"] else []
    cortes = sugerir_cortes(info["duracao"], sil, a.modo_cortes)
    lc.salvar_json(pasta / "transcricao.json", trans)
    lc.salvar_json(pasta / "silencios.json", sil)
    lc.salvar_json(pasta / "cenas.json", cenas)
    ganho = info["duracao"] - sum(b - a_ for a_, b in cortes)
    resumo = {"video": str(video), **info, "silencios": len(sil), "cenas": len(cenas) + 1,
              "palavras": sum(len(s["words"]) for s in trans), "cortes_sugeridos": cortes,
              "tempo_economizado_s": round(ganho, 2),
              "orientacao": "vertical 9:16" if info["altura"] > info["largura"] else "horizontal 16:9" if info["largura"] > info["altura"] else "quadrado 1:1"}
    lc.salvar_json(pasta / "resumo.json", resumo)
    print("\n=== RESUMO ===")
    for k in ("orientacao", "largura", "altura", "fps", "duracao", "codec", "silencios", "cenas", "palavras", "tempo_economizado_s"):
        print(f"  {k}: {resumo[k]}")
    print(f"  cortes sugeridos: {cortes}")
    print(f"\nArquivos em {pasta}")
    for s in trans[:3]:
        print(f"  [{s['start']:.1f}s] {s['text']}")


if __name__ == "__main__":
    main()
