#!/usr/bin/env python3
"""Sugere cores da marca a partir de uma imagem (logo, print do site ou foto do feed).

Uso:  rodar.py marca-cores IMAGEM [--quantas 6]
Mostra as cores mais presentes (em hex) para você escolher fundo, destaque e secundária.
"""
import argparse
import sys

import cv2
import numpy as np


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("imagem")
    ap.add_argument("--quantas", type=int, default=6)
    a = ap.parse_args()
    img = cv2.imread(a.imagem, cv2.IMREAD_UNCHANGED)
    if img is None:
        sys.exit(f"Não consegui abrir a imagem: {a.imagem}")
    if img.ndim == 3 and img.shape[2] == 4:  # ignora pixels transparentes
        img = img[img[..., 3] > 200][:, :3].reshape(-1, 1, 3)
    img = cv2.resize(img, (120, max(1, int(120 * img.shape[0] / max(1, img.shape[1])))), interpolation=cv2.INTER_AREA) if img.shape[1] > 120 else img
    dados = img.reshape(-1, 3).astype(np.float32)
    k = min(a.quantas, len(dados))
    crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.5)
    _, rot, centros = cv2.kmeans(dados, k, None, crit, 5, cv2.KMEANS_PP_CENTERS)
    cont = np.bincount(rot.flatten(), minlength=k)
    print("Cores mais presentes (da mais comum para a menos comum):")
    for i in np.argsort(-cont):
        b, g, r = [int(v) for v in centros[i]]
        print(f"  #{r:02X}{g:02X}{b:02X}   {cont[i] / cont.sum() * 100:4.1f}%")


if __name__ == "__main__":
    main()
