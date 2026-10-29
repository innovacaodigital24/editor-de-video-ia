#!/usr/bin/env python3
"""Instala a skill Editor de Vídeo IA no Claude Code e no Codex e prepara o ambiente.

Uso:
    python3 install.py                 instala para o Claude Code e para o Codex e prepara o ambiente
    python3 install.py --para claude   instala só para o Claude Code (~/.claude/skills)
    python3 install.py --para codex    instala só para o Codex (~/.agents/skills)
    python3 install.py --link          usa um link simbólico (bom para quem vai editar a skill)
    python3 install.py --sem-copia     só prepara o ambiente (usado nos testes)
    python3 install.py --destino PASTA instala em outra pasta de skills
"""
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
ORIGEM = AQUI / "skills" / "editor-de-video-ia"
PASTAS = {
    "claude": Path.home() / ".claude" / "skills",   # Claude Code
    "codex": Path.home() / ".agents" / "skills",    # Codex (CLI e app de desktop)
}


def instalar(pasta, link):
    destino = Path(pasta) / "editor-de-video-ia"
    destino.parent.mkdir(parents=True, exist_ok=True)
    if destino.is_symlink() or destino.exists():
        print(f"Atualizando a versão instalada em {destino}")
        destino.unlink() if destino.is_symlink() else shutil.rmtree(destino)
    if link:
        os.symlink(ORIGEM, destino, target_is_directory=True)
        print(f"Link criado: {destino} -> {ORIGEM}")
    else:
        shutil.copytree(ORIGEM, destino, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        print(f"Skill instalada em {destino}")
    return destino


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--para", choices=["ambos", "claude", "codex"], default="ambos")
    ap.add_argument("--destino", help="pasta de skills personalizada (ignora --para)")
    ap.add_argument("--link", action="store_true")
    ap.add_argument("--sem-copia", action="store_true")
    ap.add_argument("--sem-setup", action="store_true")
    a = ap.parse_args()
    if not ORIGEM.exists():
        sys.exit(f"Não achei {ORIGEM}. Rode este arquivo de dentro da pasta do repositório.")
    skill = ORIGEM
    if not a.sem_copia:
        if a.destino:
            pastas = [a.destino]
        else:
            pastas = [PASTAS[k] for k in (["claude", "codex"] if a.para == "ambos" else [a.para])]
        skill = [instalar(p, a.link) for p in pastas][0]
    if not a.sem_setup:
        print("\nPreparando o ambiente (uma vez só, uns 2 minutos)...\n")
        rc = subprocess.call([sys.executable, str(skill / "scripts" / "rodar.py"), "setup"])
        if rc != 0:
            sys.exit("A preparação do ambiente falhou. Veja a mensagem acima e docs/PASSO-A-PASSO.md.")
    print("\nTudo pronto.")
    print("Próximo passo: abra o Claude Code ou o Codex (app instalado no computador) em uma pasta de projeto e diga \"Edita esse vídeo\".")
    print("Se o Codex já estava aberto, feche e abra de novo para ele enxergar a skill.")
    print(f"Para conferir a instalação: python3 {skill / 'scripts' / 'rodar.py'} teste")


if __name__ == "__main__":
    main()
