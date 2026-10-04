"""Funções comuns do Editor de Vídeo IA (caminhos, ffmpeg, fontes, marca)."""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = Path(os.environ.get("EDITOR_VIDEO_IA_HOME", Path.home() / ".config" / "editor-de-video-ia"))
CONFIG_FILE = CONFIG_DIR / "config.json"


def ler_json(caminho):
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)


def salvar_json(caminho, dados):
    Path(caminho).parent.mkdir(parents=True, exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


def config():
    return ler_json(CONFIG_FILE) if CONFIG_FILE.exists() else {}


def garantir_ffmpeg():
    """Coloca ffmpeg e ffprobe no PATH (binários estáticos ou do sistema)."""
    try:
        import static_ffmpeg
        static_ffmpeg.add_paths()
    except Exception:
        pass
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        sys.exit("ffmpeg não encontrado. Rode: python3 scripts/rodar.py setup")


def rodar(cmd, check=True, capturar=False):
    """Executa um comando; em erro mostra a saída do ffmpeg em vez de esconder."""
    r = subprocess.run(cmd, stdout=subprocess.PIPE if capturar else None,
                       stderr=subprocess.PIPE, text=True)
    if check and r.returncode != 0:
        sys.exit(f"Erro ao executar: {' '.join(map(str, cmd))[:300]}\n{r.stderr[-1500:]}")
    return r


def sondar_video(caminho):
    garantir_ffmpeg()
    r = rodar(["ffprobe", "-v", "error", "-show_entries",
               "stream=codec_type,codec_name,width,height,avg_frame_rate,r_frame_rate,duration,sample_rate,channels:format=duration",
               "-of", "json", str(caminho)], capturar=True)
    d = json.loads(r.stdout)
    v = next((s for s in d["streams"] if s["codec_type"] == "video"), None)
    a = next((s for s in d["streams"] if s["codec_type"] == "audio"), None)
    if v is None:
        sys.exit("O arquivo não tem faixa de vídeo.")
    num, den = (v.get("avg_frame_rate") or "30/1").split("/")
    fps = float(num) / float(den) if float(den) else 30.0
    return {
        "largura": int(v["width"]), "altura": int(v["height"]), "fps": round(fps, 3),
        "codec": v["codec_name"], "duracao": float(d["format"]["duration"]),
        "tem_audio": a is not None, "audio_hz": int(a["sample_rate"]) if a else None,
    }


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def cor(marca, nome, padrao="#FFFFFF"):
    """Resolve uma cor da marca por nome ('destaque') ou aceita um hex direto."""
    v = marca.get("cores", {}).get(nome, nome)
    return hex_rgb(v if str(v).startswith("#") else padrao)


def procurar_pasta_sfx(projeto=None):
    """Pastas onde procurar efeitos sonoros, em ordem de prioridade."""
    pastas = []
    if projeto:
        pastas.append(Path(projeto) / "assets" / "sfx" / "pronto")
    pastas += [CONFIG_DIR / "sfx" / "pronto", SKILL_DIR / "assets" / "sfx" / "pronto"]
    return pastas


def achar_fonte(marca, papel="titulo", projeto=None):
    """Localiza o arquivo de fonte da marca. Retorna o caminho ou None."""
    f = marca.get("fontes", {})
    nomes = [f.get("arquivo_" + papel), f.get(papel)]
    candidatos = []
    for n in nomes:
        if not n:
            continue
        p = Path(n)
        candidatos += [p]
        for base in ([Path(projeto)] if projeto else []) + [CONFIG_DIR / "fonts", SKILL_DIR / "assets" / "fonts"]:
            candidatos += [base / n, base / (n + ".ttf"), base / "fonts" / n]
            if base.exists():
                peso = f.get("peso_titulo", "ExtraBold").lower()
                achados = sorted(base.glob(n.replace(" ", "") + "*.ttf"), key=lambda p: (peso not in p.name.lower(), p.name))
                candidatos += achados
    for c in candidatos:
        if c and Path(c).is_file():
            return str(c)
    padrao = CONFIG_DIR / "fonts" / ("Montserrat.ttf" if papel == "titulo" else "Inter.ttf")
    if padrao.is_file():
        return str(padrao)
    alt = CONFIG_DIR / "fonts" / "Montserrat.ttf"
    return str(alt) if alt.is_file() else None
