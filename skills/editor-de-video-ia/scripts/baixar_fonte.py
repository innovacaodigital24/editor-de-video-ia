#!/usr/bin/env python3
"""Baixa uma fonte do Google Fonts (licença livre) para usar nas legendas e cards.

Uso:  rodar.py fonte "Poppins"
Salva em ~/.config/editor-de-video-ia/fonts/. Depois use o nome em marca.json
(fontes.titulo = "Poppins") e, se for fonte estática, fontes.peso_titulo = "ExtraBold" ou "Bold".
"""
import json
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lib_common as lc

API = "https://api.github.com/repos/google/fonts/contents/ofl/{}"
PESOS = ("ExtraBold", "Bold", "Black", "SemiBold", "Medium", "Regular")


def pegar(url):
    req = urllib.request.Request(url, headers={"User-Agent": "editor-de-video-ia"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    nome = " ".join(sys.argv[1:])
    pasta = nome.lower().replace(" ", "")
    try:
        arquivos = json.loads(pegar(API.format(pasta)))
    except Exception as e:
        sys.exit(f"Não achei '{nome}' no Google Fonts ({e}). Confira o nome em fonts.google.com.")
    ttfs = [f for f in arquivos if f["name"].lower().endswith(".ttf")]
    if not ttfs:
        sys.exit("Essa família não tem arquivos .ttf no repositório.")
    variavel = [f for f in ttfs if "[" in f["name"] and "italic" not in f["name"].lower()]
    escolhidos = variavel[:1]
    if not escolhidos:
        for peso in PESOS:
            escolhidos += [f for f in ttfs if f["name"].lower().endswith(f"-{peso.lower()}.ttf")]
        escolhidos = escolhidos[:3]
    destino = lc.CONFIG_DIR / "fonts"
    destino.mkdir(parents=True, exist_ok=True)
    for f in escolhidos:
        (destino / f["name"].replace("[", "").replace("]", "").replace(",", "-")).write_bytes(pegar(f["download_url"]))
        print("baixada:", f["name"])
    print(f"\nSalvas em {destino}. Use \"{nome}\" em marca.json > fontes.titulo.")


if __name__ == "__main__":
    main()
