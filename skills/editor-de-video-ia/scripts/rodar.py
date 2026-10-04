#!/usr/bin/env python3
"""Ponto de entrada único do Editor de Vídeo IA.

Uso:  python3 scripts/rodar.py <comando> [argumentos]

Comandos: setup, analisar, validar, renderizar, marca-cores, fonte,
          sfx-sinteticos, sfx-baixar, sfx-preparar, teste
Usa o ambiente virtual criado pelo comando `setup` (só biblioteca padrão aqui).
"""
import os
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
COMANDOS = {
    "setup": "setup.py", "analisar": "analisar.py", "validar": "validar.py",
    "renderizar": "renderizar.py", "marca-cores": "marca_cores.py", "fonte": "baixar_fonte.py",
    "sfx-sinteticos": "sfx_sinteticos.py", "sfx-baixar": "sfx_baixar.py",
    "sfx-preparar": "sfx_preparar.py", "teste": "teste_rapido.py",
}


def python_do_ambiente():
    import json
    cfg = Path(os.environ.get("EDITOR_VIDEO_IA_HOME", Path.home() / ".config" / "editor-de-video-ia")) / "config.json"
    if cfg.exists():
        py = json.loads(cfg.read_text(encoding="utf-8")).get("python")
        if py and Path(py).exists():
            return py
    return None


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in COMANDOS:
        print(__doc__)
        sys.exit(0 if len(sys.argv) < 2 else 2)
    cmd, args = sys.argv[1], sys.argv[2:]
    script = str(AQUI / COMANDOS[cmd])
    py = sys.executable if cmd == "setup" else python_do_ambiente()
    if py is None:
        sys.exit("Ambiente ainda não instalado. Rode primeiro:  python3 scripts/rodar.py setup")
    sys.exit(subprocess.call([py, "-W", "ignore", script] + args))


if __name__ == "__main__":
    main()
