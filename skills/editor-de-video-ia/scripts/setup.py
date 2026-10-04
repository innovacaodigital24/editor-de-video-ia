#!/usr/bin/env python3
"""Instala o ambiente do Editor de Vídeo IA (uma vez só).

Cria um ambiente virtual isolado, instala as dependências, baixa o ffmpeg
(binário estático, sem Homebrew), baixa as fontes padrão e gera os efeitos
sonoros sintéticos. Nada é instalado fora de ~/.config/editor-de-video-ia.
"""
import argparse
import os
import subprocess
import sys
import urllib.request
import venv
from pathlib import Path

AQUI = Path(__file__).resolve().parent
HOME = Path(os.environ.get("EDITOR_VIDEO_IA_HOME", Path.home() / ".config" / "editor-de-video-ia"))
VENV = HOME / "venv"
FONTES = {
    "Montserrat.ttf": "https://github.com/google/fonts/raw/main/ofl/montserrat/Montserrat%5Bwght%5D.ttf",
    "Inter.ttf": "https://github.com/google/fonts/raw/main/ofl/inter/Inter%5Bopsz%2Cwght%5D.ttf",
}


def py_venv():
    return VENV / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def baixar(url, destino):
    destino.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "editor-de-video-ia"})
    with urllib.request.urlopen(req, timeout=60) as r, open(destino, "wb") as f:
        f.write(r.read())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sem-fontes", action="store_true", help="não baixa as fontes")
    a = ap.parse_args()
    if sys.version_info < (3, 9):
        sys.exit("Precisa de Python 3.9 ou mais novo.")
    HOME.mkdir(parents=True, exist_ok=True)
    print(f"1/5 Criando ambiente isolado em {VENV}")
    if not py_venv().exists():
        venv.EnvBuilder(with_pip=True).create(VENV)
    print("2/5 Instalando bibliotecas (pode levar alguns minutos)")
    subprocess.check_call([str(py_venv()), "-m", "pip", "install", "-q", "--upgrade", "pip"])
    subprocess.check_call([str(py_venv()), "-m", "pip", "install", "-q", "-r", str(AQUI / "requirements.txt")])
    print("3/5 Baixando o ffmpeg (binário estático)")
    subprocess.check_call([str(py_venv()), "-c",
                           "import static_ffmpeg,shutil;static_ffmpeg.add_paths();print(shutil.which('ffmpeg'))"])
    if not a.sem_fontes:
        print("4/5 Baixando fontes padrão (Montserrat e Inter, licença OFL)")
        for nome, url in FONTES.items():
            alvo = HOME / "fonts" / nome
            if not alvo.exists():
                try:
                    baixar(url, alvo)
                except Exception as e:
                    print(f"   aviso: não consegui baixar {nome} ({e}). Veja docs/SOLUCAO-DE-PROBLEMAS.md")
    print("5/5 Gerando efeitos sonoros sintéticos (livres de licença)")
    subprocess.check_call([str(py_venv()), "-W", "ignore", str(AQUI / "sfx_sinteticos.py")])
    import json
    (HOME / "config.json").write_text(json.dumps({"python": str(py_venv()), "versao": 1}, indent=2), encoding="utf-8")
    print("\nPronto. Próximo passo: abra o Claude Code numa pasta de projeto e peça \"edita esse vídeo\".")


if __name__ == "__main__":
    main()
