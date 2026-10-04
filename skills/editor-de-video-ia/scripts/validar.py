#!/usr/bin/env python3
"""Valida marca.json e plano.json ANTES de renderizar (erros claros em vez de falhas no meio do render).

Uso:  rodar.py validar --marca marca.json [--plano plano.json] [--projeto .]
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lib_common as lc

CTA_PROIBIDOS = re.compile(r"saiba mais|clique aqui|clique agora|clique no link|inscreva-?se|compre agora|link na bio|arraste para|toque aqui|swipe up", re.I)
TIPOS_CARD = {"titulo", "lista", "midia"}
FORMATOS = {"9:16", "16:9", "1:1", "4:5"}


def luminancia(rgb):
    def c(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = rgb
    return 0.2126 * c(r) + 0.7152 * c(g) + 0.0722 * c(b)


def contraste(a, b):
    la, lb = sorted((luminancia(a), luminancia(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def validar_marca(marca):
    erros, alertas = [], []
    for k in ("nome", "cores", "fontes", "legenda"):
        if k not in marca: erros.append(f"marca.json: falta '{k}'")
    cores = marca.get("cores", {})
    for k in ("fundo", "destaque", "secundaria", "texto"):
        v = cores.get(k)
        if not v or not re.fullmatch(r"#[0-9A-Fa-f]{6}", str(v)):
            erros.append(f"marca.json: cores.{k} precisa ser um hex como #1A1A1A (veio: {v!r})")
    if not erros:
        if contraste(lc.hex_rgb(cores["texto"]), lc.hex_rgb(cores["fundo"])) < 4.5:
            alertas.append("O texto tem pouco contraste com o fundo dos cards (menos de 4,5:1). Pode ficar difícil de ler no celular.")
        if contraste(lc.hex_rgb(cores["destaque"]), lc.hex_rgb(cores["fundo"])) < 3:
            alertas.append("A cor de destaque tem pouco contraste com o fundo (menos de 3:1).")
    return erros, alertas


def _textos_cards(plano):
    for c in plano.get("cards", []):
        yield c.get("rotulo", "")
        yield c.get("sub", "")
        for p in c.get("titulo", []): yield p[0]
        for it in c.get("itens", []): yield it[0]


def validar_plano(plano, marca, projeto="."):
    erros, alertas = validar_marca(marca)
    if plano.get("formato") and plano["formato"] not in FORMATOS:
        erros.append(f"plano.json: formato '{plano['formato']}' inválido (use {sorted(FORMATOS)})")
    cortes = plano.get("cortes") or []
    ant = -1
    for i, c in enumerate(cortes):
        if len(c) != 2 or c[0] >= c[1]: erros.append(f"plano.json: corte {i} inválido {c}")
        elif c[0] < ant: erros.append(f"plano.json: cortes fora de ordem ou sobrepostos no item {i}")
        else: ant = c[1]
    cards = plano.get("cards", [])
    for i, c in enumerate(cards):
        t = c.get("tipo", "titulo")
        if t not in TIPOS_CARD: erros.append(f"card {i}: tipo '{t}' inválido ({sorted(TIPOS_CARD)})"); continue
        if not (c.get("t0") is not None and c.get("t1") is not None and c["t0"] < c["t1"]): erros.append(f"card {i}: precisa de t0 < t1")
        if t == "lista" and not c.get("itens"): erros.append(f"card {i}: lista sem 'itens'")
        if t == "lista" and len(c.get("itens", [])) > 3: alertas.append(f"card {i}: mais de 3 itens fica apertado; prefira 3")
        if t == "titulo" and not c.get("titulo"): erros.append(f"card {i}: título sem 'titulo'")
        if t == "midia":
            p = Path(c.get("arquivo", ""))
            if not (p if p.is_absolute() else Path(projeto) / p).is_file(): erros.append(f"card {i}: arquivo de mídia não encontrado: {c.get('arquivo')}")
    ordenados = sorted((c for c in cards if "t0" in c and "t1" in c), key=lambda c: c["t0"])
    for a, b in zip(ordenados, ordenados[1:]):
        if b["t0"] < a["t1"]: erros.append(f"cards se sobrepõem em {b['t0']}s (um card por vez)")
    for i, ins in enumerate(plano.get("inserts", [])):
        p = Path(ins.get("arquivo", ""))
        if not (p if p.is_absolute() else Path(projeto) / p).is_file(): erros.append(f"insert {i}: arquivo não encontrado: {ins.get('arquivo')}")
        if not ins.get("t0", 0) < ins.get("t1", 0): erros.append(f"insert {i}: precisa de t0 < t1")
    for i, e in enumerate(plano.get("sfx", [])):
        if "t" not in e or "som" not in e: erros.append(f"sfx {i}: precisa de 't' e 'som'")
    regras = marca.get("regras", {})
    if regras.get("sem_botao_cta_na_tela", True):
        for txt in _textos_cards(plano):
            if CTA_PROIBIDOS.search(txt or ""):
                erros.append(f"O texto de card '{txt}' parece um botão de CTA. A marca pede nenhum botão desenhado no vídeo (a pessoa tenta clicar). Deixe o CTA só na fala.")
    evitar = [w.lower() for w in marca.get("vocabulario", {}).get("evitar", [])]
    for txt in _textos_cards(plano):
        for w in evitar:
            if w and re.search(rf"\b{re.escape(w)}\b", (txt or "").lower()):
                erros.append(f"O card usa '{w}', que está na lista de palavras a evitar da marca (o texto dos cards é criado por nós, a fala é da pessoa).")
    dur = cortes[-1][1] if cortes else None
    if dur and len(cards) / max(dur, 1) > 1 / 5:
        alertas.append("Muitos cards para a duração (mais de 1 a cada 5s). Cards demais cansam.")
    if len(plano.get("zoom", {}).get("punches", [])) > 8 and dur and dur < 60:
        alertas.append("Muitos zooms rápidos para um vídeo curto.")
    return erros, alertas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--marca", required=True)
    ap.add_argument("--plano")
    ap.add_argument("--projeto", default=".")
    a = ap.parse_args()
    marca = lc.ler_json(a.marca)
    if a.plano:
        erros, alertas = validar_plano(lc.ler_json(a.plano), marca, a.projeto)
    else:
        erros, alertas = validar_marca(marca)
    for al in alertas: print("AVISO:", al)
    for e in erros: print("ERRO:", e)
    print("OK" if not erros else f"{len(erros)} erro(s)")
    sys.exit(1 if erros else 0)


if __name__ == "__main__":
    main()
