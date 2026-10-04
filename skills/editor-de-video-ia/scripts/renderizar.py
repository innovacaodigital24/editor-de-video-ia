#!/usr/bin/env python3
"""Motor de renderização do Editor de Vídeo IA.

Lê o vídeo, a transcrição, o plano de edição (plano.json) e a marca (marca.json) e produz:
cortes de silêncio, zoom, legendas karaokê, cards no topo, mídias de apoio, efeitos sonoros,
áudio tratado (-16 LUFS), cor e a exportação final (H.264 + AAC).

Uso:
  rodar.py renderizar --video V.mov --analise saida/analise --plano plano.json --marca marca.json \
                      [--saida saida] [--nome tema] [--prontos prontos] [--preview]
"""
import argparse
import bisect
import math
import re
import shutil
import subprocess
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
import cv2
import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lib_common as lc

FPS = 30
FORMATOS = {"9:16": (1080, 1920), "16:9": (1920, 1080), "1:1": (1080, 1080), "4:5": (1080, 1350)}
IMAGENS = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
GRADES = {"natural": dict(c=1.04, s=1.0, r=0, b=0), "quente": dict(c=1.06, s=1.05, r=6, b=-8),
          "frio": dict(c=1.06, s=1.0, r=-6, b=8), "punchy": dict(c=1.08, s=1.10, r=0, b=0),
          "pb": dict(c=1.08, s=0.0, r=0, b=0)}


def ease_out(p): p = min(1.0, max(0.0, p)); return 1 - (1 - p) ** 3
def ease_io(p): p = min(1.0, max(0.0, p)); return 0.5 - 0.5 * math.cos(math.pi * p)


# ---------------------------------------------------------------- linha do tempo
class Linha:
    """Converte tempo do vídeo original em tempo do vídeo editado (depois dos cortes)."""

    def __init__(self, cortes, dur):
        cortes = cortes or [[0.0, dur]]
        self.segs = [(int(round(a * FPS)), int(round(b * FPS))) for a, b in cortes]
        self.cum, c = [], 0
        for fa, fb in self.segs:
            self.cum.append(c); c += fb - fa
        self.nfr = c
        self.mascara = {}
        for fa, fb in self.segs:
            for f in range(fa, fb):
                self.mascara[f] = True

    def manter(self, n): return n in self.mascara

    def novo(self, t):
        f = t * FPS
        for (fa, fb), c in zip(self.segs, self.cum):
            if f < fa: return c / FPS
            if f < fb: return (c + f - fa) / FPS
        return self.nfr / FPS


# ---------------------------------------------------------------- zoom
class Zoom:
    def __init__(self, kfs=None): self.kfs = sorted(kfs or [], key=lambda k: k[0])

    def __call__(self, t):
        z = 1.0
        for t0, t1, z0, z1, ea in self.kfs:
            if t >= t0:
                p = 1.0 if t1 <= t0 else min(1.0, (t - t0) / (t1 - t0))
                z = z0 + (z1 - z0) * (ease_out(p) if ea == "out" else ease_io(p))
        return z


def zoom_automatico(cortes, punches, deriva=0.05):
    """Gera zoom lento (Ken Burns) com 'punch-ins' nas palavras de peso, sem repetir o enquadramento."""
    kfs = []
    zat = lambda t: Zoom(kfs)(t)

    def add(t0, t1, z1, ea):
        if t1 <= t0: return
        kfs.append((t0, t1, zat(t0), z1, ea))

    inicios = [1.00, 1.03, 1.06]
    for si, (a, b) in enumerate(cortes):
        zs = inicios[si % 3]
        kfs.append((a, a, zs, zs, "io"))
        ps = sorted([p for p in punches if a <= p["t"] < b], key=lambda p: p["t"])
        t_cur = a
        for pi, p in enumerate(ps):
            t, alvo = p["t"], p.get("alvo", [1.11, 1.14][pi % 2])
            if t - 0.05 > t_cur + 0.3:
                add(t_cur, t - 0.05, min(zat(t_cur) + 0.03, 1.07), "io")
                t_cur = t - 0.05
            ini = max(t_cur, t - 0.05)
            add(ini, ini + 0.25, alvo, "out")
            t_cur = ini + 0.25
            prox = ps[pi + 1]["t"] if pi + 1 < len(ps) else b
            folga = prox - t_cur
            if folga > 2.2:
                t_h = t_cur + min(2.0, folga - 1.3)
                add(t_cur, t_h, alvo + 0.015, "io")
                add(t_h, t_h + 0.7, 1.03, "io")
                t_cur = t_h + 0.7
            elif folga > 0.2:
                add(t_cur, prox - 0.05, alvo + 0.01, "io")
                t_cur = prox - 0.05
        if b - t_cur > 0.3:
            add(t_cur, b, min(zat(t_cur) + deriva, 1.12), "io")
    return Zoom(kfs)


# ---------------------------------------------------------------- fontes
class Fontes:
    def __init__(self, marca, projeto):
        self.caminho = {"titulo": lc.achar_fonte(marca, "titulo", projeto), "corpo": lc.achar_fonte(marca, "corpo", projeto)}
        if not self.caminho["corpo"]: self.caminho["corpo"] = self.caminho["titulo"]
        if not self.caminho["titulo"]:
            print("AVISO: nenhuma fonte encontrada; usando fonte padrão. Rode `rodar.py setup` ou `rodar.py fonte NOME`.")
        self.peso = marca.get("fontes", {}).get("peso_titulo", "ExtraBold")
        self.cache = {}

    def get(self, papel, size, peso=None):
        peso = peso or self.peso
        k = (papel, int(round(size)), peso)
        if k not in self.cache:
            p = self.caminho.get(papel)
            if p is None:
                try:
                    f = ImageFont.load_default(int(round(size)))
                except TypeError:
                    f = ImageFont.load_default()
            else:
                f = ImageFont.truetype(p, int(round(size)))
                try:
                    f.set_variation_by_name(peso)
                except Exception:
                    pass  # fonte estática: usa o peso do arquivo
            self.cache[k] = f
        return self.cache[k]


# ---------------------------------------------------------------- mídia (imagem ou vídeo de apoio)
class Midia:
    def __init__(self, caminho):
        self.img, self.cap, self.last = None, None, -2
        if Path(caminho).suffix.lower() in IMAGENS:
            self.img = np.array(Image.open(caminho).convert("RGB"))
        else:
            self.cap = cv2.VideoCapture(str(caminho))
            self.n = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1
            self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30

    def frame(self, rel):
        if self.img is not None: return self.img
        idx = int(rel * self.fps) % self.n
        if idx != self.last + 1: self.cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ok, fr = self.cap.read()
        if not ok:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0); ok, fr = self.cap.read(); idx = 0
        self.last = idx
        return cv2.cvtColor(fr, cv2.COLOR_BGR2RGB)


def cobrir(img, w, h, zoom=1.0):
    ih, iw = img.shape[:2]
    s = max(w / iw, h / ih) * zoom
    r = cv2.resize(img, (max(1, int(iw * s)), max(1, int(ih * s))), interpolation=cv2.INTER_AREA if s < 1 else cv2.INTER_CUBIC)
    y0, x0 = (r.shape[0] - h) // 2, (r.shape[1] - w) // 2
    return r[y0:y0 + h, x0:x0 + w]


def misturar(frame, camada, y, x=0):
    """Mistura (rgb, alfa) sobre o quadro na posição (x, y)."""
    rgb, a = camada
    h, w = rgb.shape[:2]
    H_, W_ = frame.shape[:2]
    y1, y2, x1, x2 = max(0, y), min(H_, y + h), max(0, x), min(W_, x + w)
    if y2 <= y1 or x2 <= x1: return
    sub = frame[y1:y2, x1:x2].astype(np.float32)
    r, aa = rgb[y1 - y:y2 - y, x1 - x:x2 - x], a[y1 - y:y2 - y, x1 - x:x2 - x]
    frame[y1:y2, x1:x2] = np.clip(sub * (1 - aa) + r * aa, 0, 255).astype(np.uint8)


# ---------------------------------------------------------------- legendas
class Legendas:
    def __init__(self, W, H, marca, fontes, palavras, linha):
        self.W, self.H, self.f = W, H, fontes
        cfg = marca.get("legenda", {})
        self.estilo = cfg.get("estilo", "karaoke")
        self.U = min(W, H) / 1080
        retrato = H >= W
        self.tam = cfg.get("tamanho", 84) * (1 if retrato else 0.8)
        self.pos = cfg.get("posicao_vertical", 0.78 if retrato else 0.86)
        self.contorno = cfg.get("contorno", 6)
        self.alta = cfg.get("caixa_alta", True)
        self.cor_ativa = lc.cor(marca, cfg.get("cor_ativa", "destaque"))
        self.cor_texto = lc.cor(marca, "texto")
        self.seguro = (0.80 if retrato else 0.60) * W
        self.destaque = {self._limpa(p) for p in marca.get("palavras_destaque", [])}
        self.banda = int(380 * self.U)
        self.cache = {}
        maxn = cfg.get("palavras_por_tela", 4) if self.estilo == "karaoke" else 8
        self.palavras = []
        for w in palavras:
            t = self._limpa(w["w"])
            if not t: continue
            self.palavras.append({"txt": t, "brk": w["w"][-1:] in ",.?!;:", "s": w["s"], "e": w["e"],
                                  "ns": linha.novo(w["s"]), "ne": linha.novo(w["e"])})
        for i in range(len(self.palavras) - 1):
            self.palavras[i]["ne"] = min(self.palavras[i]["ne"], self.palavras[i + 1]["ns"])
        grupos, cur = [], []
        for i, w in enumerate(self.palavras):
            cur.append(w)
            gap = (self.palavras[i + 1]["s"] - w["e"]) if i + 1 < len(self.palavras) else 9
            if len(cur) >= maxn or w["brk"] or gap > 0.4:
                grupos.append(cur); cur = []
        if cur: grupos.append(cur)
        self.grupos = []
        for gi, g in enumerate(grupos):
            prox = grupos[gi + 1][0]["ns"] if gi + 1 < len(grupos) else 1e9
            self.grupos.append({"w": g, "s": g[0]["ns"], "e": min(prox, g[-1]["ne"] + 0.25)})

    def _limpa(self, t):
        t = "".join(c for c in t if c.isalnum() or c in "?-'")
        return t.upper() if self.alta else t

    def _peso(self, txt): return any(ch.isdigit() for ch in txt) or txt.upper() in {d.upper() for d in self.destaque}

    def camada(self, gi, ai, pop):
        chave = (gi, ai, pop)
        if chave in self.cache: return self.cache[chave]
        ws = self.grupos[gi]["w"]
        esc = lambda i: (1.2 if self._peso(ws[i]["txt"]) else 1.12) if (i == ai and pop) else 1.0

        def layout(sz):
            sp = self.f.get("titulo", sz).getlength(" ")
            wd = [self.f.get("titulo", sz * esc(i)).getlength(ws[i]["txt"]) for i in range(len(ws))]
            linhas = [list(range(len(ws)))]
            if sum(wd) + sp * (len(ws) - 1) > self.seguro and len(ws) > 1:
                h = math.ceil(len(ws) / 2); linhas = [list(range(h)), list(range(h, len(ws)))]
            mx = max(sum(wd[i] for i in l) + sp * (len(l) - 1) for l in linhas)
            return sp, wd, linhas, mx

        sz = self.tam
        sp, wd, linhas, mx = layout(sz)
        if mx > self.seguro:
            sz = sz * self.seguro / mx
            sp, wd, linhas, mx = layout(sz)
        lay = Image.new("RGBA", (self.W, self.banda), (0, 0, 0, 0))
        sombra = Image.new("RGBA", (self.W, self.banda), (0, 0, 0, 0))
        d, ds = ImageDraw.Draw(lay), ImageDraw.Draw(sombra)
        lh = sz * 1.15
        y0 = self.banda / 2 - (len(linhas) - 1) * lh / 2
        sw = int(self.contorno * self.U)
        for li, idxs in enumerate(linhas):
            lw = sum(wd[i] for i in idxs) + sp * (len(idxs) - 1)
            x = self.W / 2 - lw / 2
            base = y0 + li * lh + sz * 0.35
            for i in idxs:
                ativo = (i == ai) and self.estilo == "karaoke"
                fz = self.f.get("titulo", sz * esc(i))
                cx = x + wd[i] / 2
                col = self.cor_ativa if ativo else self.cor_texto
                ds.text((cx, base + 8 * self.U), ws[i]["txt"], font=fz, fill=(0, 0, 0, 150), anchor="ms", stroke_width=sw, stroke_fill=(0, 0, 0, 150))
                d.text((cx, base), ws[i]["txt"], font=fz, fill=col + (255,), anchor="ms", stroke_width=sw, stroke_fill=(0, 0, 0, 255))
                x += wd[i] + sp
        sombra = sombra.filter(ImageFilter.GaussianBlur(5 * self.U))
        sombra.alpha_composite(lay)
        arr = np.asarray(sombra).astype(np.float32)
        out = (arr[..., :3], arr[..., 3:4] / 255.0)
        if len(self.cache) > 400: self.cache.clear()
        self.cache[chave] = out
        return out

    def aplicar(self, frame, tn):
        for gi, g in enumerate(self.grupos):
            if g["s"] <= tn < g["e"]:
                ai = -1
                if self.estilo == "karaoke":
                    ai = 0
                    for i, w in enumerate(g["w"]):
                        if w["ns"] <= tn: ai = i
                pop = ai >= 0 and int((tn - g["w"][ai]["ns"]) * FPS) < 3
                misturar(frame, self.camada(gi, ai, pop), int(self.pos * self.H - self.banda / 2))
                return


# ---------------------------------------------------------------- cards
class Cards:
    """Cards informativos: 'titulo', 'lista' (itens que entram com a fala) e 'midia' (imagem/vídeo)."""

    def __init__(self, W, H, marca, fontes, cards, linha, projeto):
        self.W, self.H, self.f, self.m = W, H, fontes, marca
        self.retrato = H >= W
        self.U = min(W, H) / 1080
        self.dark = lc.cor(marca, "fundo")
        self.lime = lc.cor(marca, "destaque")
        self.gold = lc.cor(marca, "secundaria")
        self.txt = lc.cor(marca, "texto")
        self.cw = int(960 * self.U) if self.retrato else int(0.40 * W)
        self.x = (W - self.cw) // 2 if self.retrato else int(0.05 * W)
        self.y = int((0.102 if self.retrato else 0.07) * H)
        self.cards, self.cache = [], {}
        for c in cards or []:
            c = dict(c)
            c["n0"], c["n1"] = linha.novo(c["t0"]), linha.novo(c["t1"])
            tipo = c.get("tipo", "titulo")
            c["h"] = int({"titulo": 210, "lista": 292, "midia": 300}[tipo] * self.U)
            c["zf"] = c.get("zoom_minimo", {"titulo": 1.06, "lista": 1.11, "midia": 1.14}[tipo])
            if tipo == "lista": c["it"] = [(t, linha.novo(ts)) for t, ts in c["itens"]]
            if tipo == "midia":
                p = Path(c["arquivo"])
                if not p.is_absolute() and projeto: p = Path(projeto) / p
                c["_midia"] = Midia(p)
            self.cards.append(c)

    def ativo(self, tn):
        for k, c in enumerate(self.cards):
            if c["n0"] <= tn <= c["n1"]:
                vis = ease_out((tn - c["n0"]) / 0.45) * ease_out((c["n1"] - tn) / 0.3)
                return k, vis
        return -1, 0.0

    def _encaixar(self, txt, papel, tam, maxw, peso=None):
        t = tam
        while t > 14 and self.f.get(papel, t, peso).getlength(txt) > maxw: t -= 2
        return self.f.get(papel, t, peso)

    def conteudo(self, ci, ps, tn=0.0):
        c = self.cards[ci]; U = self.U
        ps = list(ps)
        chave = (ci, tuple(int(p * 6) for p in ps), int(tn * FPS) if c.get("tipo") == "midia" else 0)
        if chave in self.cache: return self.cache[chave]
        tipo = c.get("tipo", "titulo")
        CH = c["h"] if tipo != "lista" else int((110 + max(1, sum(1 for p in ps if p > 0)) * 54 + 20) * U)
        ox, oy, CW = 0, int(20 * U), self.cw
        tela = (CW + int(40 * U), c["h"] + int(40 * U))
        ox = int(20 * U)
        sh = Image.new("RGBA", tela, (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle((ox, oy + 8 * U, ox + CW, oy + CH + 8 * U), radius=int(34 * U), fill=(0, 0, 0, 130))
        sh = sh.filter(ImageFilter.GaussianBlur(10 * U))
        lay = Image.new("RGBA", tela, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        d.rounded_rectangle((ox, oy, ox + CW, oy + CH), radius=int(34 * U), fill=self.dark + (242,), outline=self.gold + (95,), width=2)
        if tipo == "midia":
            fr = cobrir(c["_midia"].frame(max(0.0, tn - c["n0"])), CW, CH)
            mask = Image.new("L", (CW, CH), 0)
            ImageDraw.Draw(mask).rounded_rectangle((0, 0, CW, CH), radius=int(34 * U), fill=255)
            lay.paste(Image.fromarray(fr), (ox, oy), mask)
        else:
            d.rounded_rectangle((ox + 30 * U, oy + 30 * U, ox + 37 * U, oy + 62 * U), radius=3, fill=self.lime + (255,))
            x = ox + 54 * U
            fl = self.f.get("corpo", 31 * U, "ExtraBold")
            for ch in c.get("rotulo", ""):
                d.text((x, oy + 60 * U), ch, font=fl, fill=self.gold + (255,), anchor="ls"); x += fl.getlength(ch) + 5 * U
            if tipo == "titulo":
                partes = c.get("titulo", [])
                full = "".join(p[0] for p in partes)
                ft = self._encaixar(full, "titulo", 60 * U, CW - 90 * U)
                x = ox + 44 * U
                for txt, hl in partes:
                    d.text((x, oy + 132 * U), txt, font=ft, fill=(self.lime if hl else self.txt) + (255,), anchor="ls"); x += ft.getlength(txt)
                if c.get("sub"):
                    d.text((ox + 46 * U, oy + 180 * U), c["sub"], font=self.f.get("corpo", 30 * U, "Medium"), fill=(200, 200, 200, 255), anchor="ls")
            else:
                for i, ((txt, _), p) in enumerate(zip(c["itens"], ps)):
                    if p <= 0: continue
                    cy = oy + (110 + i * 54 + 24) * U; sx = (1 - p) * 26 * U; a = int(255 * p)
                    cx = ox + 62 * U + sx
                    d.ellipse((cx - 16 * U, cy - 16 * U, cx + 16 * U, cy + 16 * U), fill=self.lime + (a,))
                    d.line([(cx - 7 * U, cy), (cx - 2 * U, cy + 6 * U), (cx + 8 * U, cy - 6 * U)], fill=self.dark + (a,), width=max(2, int(4 * U)), joint="curve")
                    ft = self._encaixar(txt, "titulo", 38 * U, CW - 140 * U)
                    d.text((ox + 96 * U + sx, cy + 14 * U), txt, font=ft, fill=self.txt + (a,), anchor="ls")
        sh.alpha_composite(lay)
        arr = np.asarray(sh).astype(np.float32)
        out = (arr[..., :3], arr[..., 3:4] / 255.0)
        if len(self.cache) > 300: self.cache.clear()
        self.cache[chave] = out
        return out

    def aplicar(self, frame, k, vis, tn):
        c = self.cards[k]
        ps = [ease_out((tn - it[1]) / 0.3) for it in c["it"]] if c.get("tipo") == "lista" else []
        rgb, al = self.conteudo(k, ps, tn)
        misturar(frame, (rgb, al * vis), y=self.y - int(20 * self.U) + int((1 - vis) * -40 * self.U), x=self.x - int(20 * self.U))


# ---------------------------------------------------------------- cabeça (para o card não cobrir o rosto)
def estimar_cabeca(video, W, H, dur):
    """Estima onde fica o topo da cabeça (px) para o enquadramento abrir espaço aos cards."""
    try:
        det = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        topos = []
        for k in range(1, 9):
            r = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{dur * k / 9:.2f}", "-i", str(video), "-frames:v", "1",
                                "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}", "-f", "image2pipe", "-vcodec", "png", "-"],
                               stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            if not r.stdout: continue
            img = cv2.imdecode(np.frombuffer(r.stdout, np.uint8), cv2.IMREAD_GRAYSCALE)
            rostos = det.detectMultiScale(img, 1.15, 5, minSize=(int(W * 0.12), int(W * 0.12)))
            if len(rostos):
                x, y, w, h = max(rostos, key=lambda r_: r_[2] * r_[3])
                topos.append(y - 0.45 * h)
        if topos: return float(np.median(topos))
    except Exception:
        pass
    return 0.24 * H


# ---------------------------------------------------------------- cor
def aplicar_cor(fr, grade, lut, vinheta):
    g = GRADES.get(grade, GRADES["natural"])
    if g["s"] == 1.0 and g["r"] == 0 and g["b"] == 0:
        fr = lut[fr]
    else:
        f = fr.astype(np.float32)
        cinza = f.mean(axis=2, keepdims=True)
        f = cinza + (f - cinza) * g["s"]
        f[..., 0] += g["r"]; f[..., 2] += g["b"]
        f = (f - 128) * g["c"] + 128
        fr = np.clip(f, 0, 255).astype(np.uint8)
    if vinheta is not None:
        fr = (fr.astype(np.float32) * vinheta).astype(np.uint8)
    return np.ascontiguousarray(fr)


# ---------------------------------------------------------------- áudio
def achar_sfx(nome, projeto):
    p = Path(nome)
    if p.suffix == ".wav" and p.is_file(): return p
    for pasta in lc.procurar_pasta_sfx(projeto):
        for cand in (pasta / f"{nome}.wav", pasta / nome):
            if cand.is_file(): return cand
        achados = sorted(pasta.glob(f"*{nome}*.wav")) if pasta.exists() else []
        if achados: return achados[0]
    return None


def montar_audio(video, linha, plano, projeto, saida_dir, info, avisos):
    SR = 48000
    N = int(linha.nfr / FPS * SR)
    alvo = plano.get("audio", {}).get("lufs", -16)
    voz = np.zeros((N, 2), np.float32)
    if info["tem_audio"]:
        fc = ""
        for i, (fa, fb) in enumerate(linha.segs):
            ta, tb = fa / FPS, min(fb / FPS, info["duracao"])
            fc += f"[0:a]atrim={ta}:{tb},asetpts=PTS-STARTPTS,afade=t=in:d=0.01,afade=t=out:st={max(0, tb - ta - 0.01)}:d=0.01[a{i}];"
        ins = "".join(f"[a{i}]" for i in range(len(linha.segs)))
        cadeia = f"{ins}concat=n={len(linha.segs)}:v=0:a=1"
        if plano.get("audio", {}).get("highpass", 80): cadeia += f",highpass=f={plano.get('audio', {}).get('highpass', 80)}"
        if plano.get("audio", {}).get("compressor", True): cadeia += ",acompressor=threshold=-18dB:ratio=3:attack=10:release=150:makeup=2"
        cadeia += f",loudnorm=I={alvo}:TP=-1.5:LRA=11,aresample={SR},aformat=channel_layouts=stereo[v]"
        wav = Path(saida_dir) / "voz.wav"
        lc.rodar(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-filter_complex", fc + cadeia, "-map", "[v]", "-c:a", "pcm_f32le", str(wav)])
        v, _ = sf.read(str(wav), dtype="float32")
        voz[:min(N, len(v))] = v[:N]
    sfx = np.zeros(N, np.float32)
    for e in plano.get("sfx", []):
        arq = achar_sfx(e["som"], projeto)
        if arq is None:
            avisos.append(f"som não encontrado: {e['som']}"); continue
        x, _ = sf.read(str(arq))
        m = x.mean(axis=1) if x.ndim > 1 else x
        m = m / (np.abs(m).max() + 1e-9) * 10 ** (e.get("pico_db", -16) / 20)
        i = int(max(0, linha.novo(e["t"]) * SR))
        fim = min(N, i + len(m))
        if fim > i: sfx[i:fim] += m[:fim - i].astype(np.float32)
    mix = voz + sfx[:, None]
    fade = np.ones(N, np.float32)
    fo, fi = int(plano.get("fade_out", 0.3) * SR), int(0.05 * SR)
    if fo: fade[-fo:] = np.linspace(1, 0, fo)
    fade[:fi] = np.linspace(0, 1, fi)
    mix = np.clip(mix * fade[:, None], -0.99, 0.99)
    final = Path(saida_dir) / "audio_final.wav"
    sf.write(str(final), mix, SR, subtype="PCM_24")
    return final


# ---------------------------------------------------------------- legendas em arquivo
def tempo_srt(t):
    h, m, s = int(t // 3600), int(t % 3600 // 60), t % 60
    return f"{h:02d}:{m:02d}:{int(s):02d},{int((s % 1) * 1000):03d}"


def tempo_ass(t):
    h, m, s = int(t // 3600), int(t % 3600 // 60), t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def escrever_legendas(leg, marca, W, H, base):
    with open(f"{base}.srt", "w", encoding="utf-8") as f:
        for i, g in enumerate(leg.grupos, 1):
            f.write(f"{i}\n{tempo_srt(g['s'])} --> {tempo_srt(g['e'])}\n{' '.join(w['txt'] for w in g['w'])}\n\n")
    bgr = lambda rgb: "&H00%02X%02X%02X" % (rgb[2], rgb[1], rgb[0])
    fonte = marca.get("fontes", {}).get("titulo", "Montserrat") + " ExtraBold"
    marg = int(H * (1 - leg.pos) - leg.tam * 0.6)
    with open(f"{base}.ass", "w", encoding="utf-8") as f:
        f.write(f"[Script Info]\nScriptType: v4.00+\nPlayResX: {W}\nPlayResY: {H}\n\n[V4+ Styles]\n"
                "Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding\n"
                f"Style: Karaoke,{fonte},{int(leg.tam)},{bgr(leg.cor_ativa)},{bgr(leg.cor_texto)},&H00000000,&H96000000,0,0,0,0,100,100,0,0,1,{leg.contorno},2,2,{int(W * 0.1)},{int(W * 0.1)},{marg},1\n\n"
                "[Events]\nFormat: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text\n")
        for g in leg.grupos:
            txt = ""
            for j, w in enumerate(g["w"]):
                nxt = g["w"][j + 1]["ns"] if j + 1 < len(g["w"]) else g["e"]
                txt += "{\\k%d}%s " % (max(1, round((nxt - w["ns"]) * 100)), w["txt"])
            f.write(f"Dialogue: 0,{tempo_ass(g['s'])},{tempo_ass(g['e'])},Karaoke,,0,0,0,,{txt.strip()}\n")


def proxima_versao(pasta, nome):
    pasta = Path(pasta)
    v = [int(m.group(1)) for p in pasta.glob(f"{nome}_v*.mp4") if (m := re.match(rf"{re.escape(nome)}_v(\d+)", p.stem))]
    return (max(v) + 1) if v else 1


# ---------------------------------------------------------------- principal
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--analise", default="saida/analise")
    ap.add_argument("--plano", required=True)
    ap.add_argument("--marca", required=True)
    ap.add_argument("--saida", default="saida")
    ap.add_argument("--nome", default=None)
    ap.add_argument("--prontos", default=None, help="pasta de entrega; salva como nome_vN sem sobrescrever")
    ap.add_argument("--projeto", default=".", help="pasta do projeto (para achar assets/ e fontes)")
    ap.add_argument("--preview", action="store_true", help="render rápido de baixa qualidade para conferir")
    a = ap.parse_args()
    lc.garantir_ffmpeg()
    import validar
    marca, plano = lc.ler_json(a.marca), lc.ler_json(a.plano)
    erros, alertas = validar.validar_plano(plano, marca, a.projeto)
    for al in alertas: print("AVISO:", al)
    if erros:
        sys.exit("Plano inválido:\n  - " + "\n  - ".join(erros))
    video = Path(a.video)
    info = lc.sondar_video(video)
    fmt = plano.get("formato") or ("9:16" if info["altura"] > info["largura"] else "16:9")
    W, H = FORMATOS[fmt]
    retrato = H >= W
    nome = a.nome or plano.get("titulo", "video")
    saida = Path(a.saida); saida.mkdir(parents=True, exist_ok=True)
    trans = lc.ler_json(Path(a.analise) / "transcricao.json") if (Path(a.analise) / "transcricao.json").exists() else []
    palavras = [w for s in trans for w in s["words"]]
    cortes = plano.get("cortes") or [[0.0, info["duracao"]]]
    linha = Linha(cortes, info["duracao"])
    fontes = Fontes(marca, a.projeto)
    leg_cfg = plano.get("legendas", {}).get("ativa", True)
    leg = Legendas(W, H, marca, fontes, palavras, linha) if (leg_cfg and palavras and marca.get("legenda", {}).get("estilo", "karaoke") != "nenhuma") else None
    cards = Cards(W, H, marca, fontes, plano.get("cards"), linha, a.projeto)
    zp = plano.get("zoom", {})
    if zp.get("keyframes"):
        zoom = Zoom([tuple(k) for k in zp["keyframes"]])
    else:
        zoom = zoom_automatico(cortes, zp.get("punches", []), zp.get("deriva", 0.05))
    cabeca = estimar_cabeca(video, W, H, info["duracao"]) if cards.cards and retrato else 0.24 * H
    OX, OY = W / 2, 0.42 * H
    inserts = []
    for ins in plano.get("inserts", []):
        p = Path(ins["arquivo"])
        if not p.is_absolute(): p = Path(a.projeto) / p
        inserts.append({**ins, "n0": linha.novo(ins["t0"]), "n1": linha.novo(ins["t1"]), "m": Midia(p)})
    grade = plano.get("cor", "natural")
    c_ = GRADES.get(grade, GRADES["natural"])["c"]
    lut = np.clip((np.arange(256) - 128) * c_ + 128, 0, 255).astype(np.uint8)
    vinheta = None
    if plano.get("vinheta"):
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        vinheta = (1 - 0.15 * (((xx / W - 0.5) ** 2 + (yy / H - 0.5) ** 2) * 2))[..., None]
    print(f"Renderizando {linha.nfr} quadros ({linha.nfr / FPS:.1f}s) em {fmt} ({W}x{H})")
    sem_audio = saida / f"{nome}_sem_audio.mp4"
    preset, crf = ("veryfast", "24") if a.preview else ("slow", "18")
    leitor = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(video), "-an", "-vf",
                               f"fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},scale=in_color_matrix=bt709:in_range=tv",
                               "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE, bufsize=W * H * 3 * 2)
    gravador = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                                 "-vf", "scale=out_color_matrix=bt709:out_range=tv", "-c:v", "libx264", "-preset", preset, "-crf", crf, "-pix_fmt", "yuv420p",
                                 "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-movflags", "+faststart", str(sem_audio)],
                                stdin=subprocess.PIPE)
    k, total_src = 0, int(info["duracao"] * FPS) + 2
    for n in range(total_src):
        buf = leitor.stdout.read(W * H * 3)
        if len(buf) < W * H * 3: break
        if not linha.manter(n): continue
        ts, tn = n / FPS, k / FPS
        fr = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
        ci, vis = cards.ativo(tn)
        z = zoom(ts); dy = 0.0
        if ci >= 0:
            z = max(z, 1 + (cards.cards[ci]["zf"] - 1) * vis)
            if retrato:
                precisa = max(0, cards.y + cards.cards[ci]["h"] + 24 * cards.U - (OY + (cabeca - OY) * z))
                dy = min(precisa, OY * (z - 1) - 2) * vis
        M = np.float32([[z, 0, OX * (1 - z)], [0, z, OY * (1 - z) + dy]])
        fr = cv2.warpAffine(fr, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        fr = aplicar_cor(fr, grade, lut, vinheta)
        for ins in inserts:
            if ins["n0"] <= tn <= ins["n1"]:
                al = ease_out((tn - ins["n0"]) / 0.25) * ease_out((ins["n1"] - tn) / 0.25)
                dur = max(0.1, ins["n1"] - ins["n0"])
                z_i = 1.0 + 0.06 * (tn - ins["n0"]) / dur
                img = cobrir(ins["m"].frame(tn - ins["n0"]), W, H, z_i)
                fr = (fr.astype(np.float32) * (1 - al) + img.astype(np.float32) * al).astype(np.uint8)
        if ci >= 0 and vis > 0.01: cards.aplicar(fr, ci, vis, tn)
        if leg is not None: leg.aplicar(fr, tn)
        esq = linha.nfr - 1 - k
        fade = int(plano.get("fade_out", 0.3) * FPS)
        if fade and esq < fade:
            fr = (fr.astype(np.float32) * (esq + 1) / (fade + 1)).astype(np.uint8)
        gravador.stdin.write(fr.tobytes())
        k += 1
        if k % 150 == 0: print(f"  {k}/{linha.nfr} quadros", flush=True)
    gravador.stdin.close(); gravador.wait(); leitor.stdout.close(); leitor.wait()
    if gravador.returncode != 0 or k == 0:
        sys.exit("Falha ao gravar o vídeo. Veja as mensagens do ffmpeg acima.")
    avisos = []
    print("Tratando o áudio e mixando efeitos sonoros")
    audio = montar_audio(video, linha, plano, a.projeto, saida, info, avisos)
    final = saida / f"{nome}.mp4"
    lc.rodar(["ffmpeg", "-v", "error", "-y", "-i", str(sem_audio), "-i", str(audio), "-c:v", "copy", "-c:a", "aac", "-b:a", "320k",
              "-ar", "48000", "-movflags", "+faststart", "-shortest", str(final)])
    if leg is not None: escrever_legendas(leg, marca, W, H, str(saida / nome))
    sem_audio.unlink(missing_ok=True)
    entregue = final
    if a.prontos:
        pr = Path(a.prontos); pr.mkdir(parents=True, exist_ok=True)
        v = proxima_versao(pr, nome)
        entregue = pr / f"{nome}_v{v}.mp4"
        shutil.copy2(final, entregue)
        for ext in (".srt", ".ass"):
            if (saida / f"{nome}{ext}").exists(): shutil.copy2(saida / f"{nome}{ext}", pr / f"{nome}_v{v}{ext}")
    for av in avisos: print("AVISO:", av)
    print(f"\nPRONTO: {entregue}")


if __name__ == "__main__":
    main()
