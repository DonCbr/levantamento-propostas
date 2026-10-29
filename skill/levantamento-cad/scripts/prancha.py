# Prancha padrao de proposta, no modelo "PROPOSTA DE LAYOUT" (ref.: PROPOSTA_ELAINE_R03_PROPOSTA.pdf):
# planta baixa humanizada 1:50 com cotas, legenda de materiais, quadro de areas, quadro de mobiliario e carimbo.
# Planta em raster 300 dpi; textos, cotas, quadros e carimbo vetoriais em Arial (pymupdf).
# Geometria em cm no referencial da folha do levantamento; a vista espelha x como no CAD (X = -x).
import math, io
import numpy as np
import pymupdf
from PIL import Image, ImageDraw, ImageFilter
from shapely.geometry import Polygon, LineString
from shapely.ops import unary_union

MM = 72 / 25.4
DPI = 300
ARIAL, ARIAL_B = "C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/arialbd.ttf"
F_REG, F_BOLD = pymupdf.Font(fontfile=ARIAL), pymupdf.Font(fontfile=ARIAL_B)
VERM, PRETO, CINZA = (0.80, 0.05, 0.05), (0.13, 0.13, 0.13), (0.38, 0.38, 0.38)
LINHA_TAB = (0.72, 0.72, 0.72)

# ---------------- materiais (paleta do modelo: cores claras, so a grade das placas) ----------------
def _h2(a, b, seed):
    x = (a.astype(np.int64) * 73856093) ^ (b.astype(np.int64) * 19349663) ^ (seed * 83492791)
    return (x % 10007) / 10007.0

def _cor(c, U): return np.broadcast_to(np.array(c, float), U.shape + (3,)).copy()

def _grade(base, linha, passo):
    def f(U, V, s):
        t = passo * s; out = _cor(base, U)
        out[((U % t) < 2) | ((V % t) < 2)] = linha
        return out
    return f

def _deck(U, V, s):
    out = _cor((196, 153, 106), U); t = 14 * s
    row = (V // t).astype(np.int64); off = (_h2(row, row * 0 + 3, 4) * 180 * s)
    out[((V % t) < 2) | (((U + off) % (180 * s)) < 2)] = (164, 122, 80)
    return out

def _gramado(U, V, s):
    out = _cor((147, 184, 105), U); t = 70 * s
    out[(((U + V) % t) < 2.5) | (((U - V) % t) < 2.5)] = (132, 170, 93)
    return out

def _pedrisco(U, V, s):
    out = _cor((231, 222, 204), U)
    out[_h2(U // 3, V // 3, 8) > 0.93] = (203, 190, 168)
    return out

def _piscina(U, V, s):
    t = ((U - U.min()) + (V - V.min())) / max(1, (U.max() - U.min()) + (V.max() - V.min()))
    out = np.array((142, 207, 238))[None, None, :] * (1 - t[..., None]) + np.array((74, 160, 218))[None, None, :] * t[..., None]
    k = np.sin(U * 0.05 + 2.5 * np.sin(V * 0.04)) * np.sin(V * 0.045 + 2 * np.sin(U * 0.03))
    return out + (k > 0.8)[..., None] * 22

def _travertino(U, V, s):
    out = _cor((234, 222, 199), U); out[(V % (3 * s)) < 1] = (222, 208, 182)
    return out

MAT = {
    "porc90": _grade((239, 235, 229), (219, 214, 206), 90), "porc60": _grade((242, 242, 240), (221, 221, 217), 60),
    "box": _grade((231, 234, 234), (209, 213, 213), 30), "drenante": _grade((215, 213, 209), (195, 193, 188), 50),
    "pedra": _grade((237, 231, 221), (214, 206, 193), 50), "concreto": _grade((220, 218, 214), (201, 199, 195), 100),
    "deck": _deck, "gramado": _gramado, "pedrisco": _pedrisco, "piscina": _piscina, "travertino": _travertino,
}
LEGENDA_PADRAO = {   # tipo -> texto (o projeto escolhe quais entram)
    "parede": "PAREDE (ALVENARIA)", "porc90": "PORCELANATO 90×90 – ÁREAS SECAS", "porc60": "PORCELANATO 60×60 – ÁREAS MOLHADAS",
    "deck": "DECK DE MADEIRA", "drenante": "PISO DRENANTE", "pedra": "PEDRA NATURAL", "concreto": "CALÇADA EM CONCRETO",
    "travertino": "TRAVERTINO (BANCADAS)", "piscina": "PISCINA", "gramado": "JARDIM / GRAMADO",
    "pedrisco": "CANTEIRO (PEDRISCO CLARO) E PAISAGISMO", "projecao": "PROJEÇÃO DA COBERTURA", "esquadria": "ESQUADRIAS / VIDRO",
}

# ---------------- mobiliario: estilo -> (preenchimento, contorno) ----------------
COR = {
    "cama": ((242, 238, 229), (186, 180, 168)), "travesseiro": ((252, 252, 250), (196, 196, 190)),
    "lencol": ((233, 227, 215), (190, 182, 168)), "manta": ((196, 128, 96), (168, 104, 76)),
    "madeira": ((202, 167, 123), (158, 124, 86)), "mesa": ((188, 148, 103), (140, 106, 70)),
    "armario": ((207, 172, 126), (160, 126, 88)), "estofado2": ((226, 220, 208), (176, 168, 156)),
    "almofada": ((237, 232, 223), (188, 182, 172)), "almofada_clara": ((250, 250, 247), (190, 188, 182)),
    "tapete": ((214, 209, 201), None), "tv": ((40, 40, 42), None), "inox": ((216, 219, 222), (150, 155, 160)),
    "inox_escuro": ((46, 46, 48), None), "loucas": ((255, 255, 255), (150, 150, 150)), "loucas2": ((236, 241, 244), (178, 182, 186)),
    "cadeira": ((122, 90, 66), (86, 62, 44)), "vidro": ((206, 227, 238), (140, 170, 190)),
    "carro": ((240, 240, 238), (150, 150, 150)), "carro2": ((222, 224, 226), (160, 160, 160)), "vidro_carro": ((62, 72, 84), None),
    "pedra": ((226, 219, 206), (180, 172, 158)), "luminaria": ((250, 241, 212), (205, 190, 150)),
    "box": (None, (176, 190, 196)), "ralo": ((140, 140, 140), None),
}
SEM_SOMBRA = {"tapete", "box", "ralo", "linha", "vidro_linha", "pedra", "queimador", "loucas2", "inox", "inox_escuro",
              "vidro", "vidro_carro", "luminaria", "manta", "travesseiro", "lencol", "almofada", "carro2", "tv"}

def _polys(g):
    if g is None or g.is_empty: return []
    return [p for p in (g.geoms if hasattr(g, "geoms") else [g]) if isinstance(p, Polygon) and p.area > 0.5]


class Prancha:
    """cfg: dict com lote, escala, folha, posicao da planta, ambientes, pisos, pecas, paredes, esquadrias, portas,
    rotulos, cotas, quadros e carimbo (ver prancha04.py)."""

    def __init__(self, cfg):
        self.c = cfg
        self.k = 10.0 / cfg["escala"]                    # mm de papel por cm real
        self.s = self.k * DPI / 25.4                     # px por cm real
        x0, y0, x1, y1 = cfg["lote"].bounds
        self.xr, self.yr = x1, y1                        # canto do lote no topo-esquerda da vista (rua, divisa do corredor)
        self.PX, self.PY = cfg["planta_mm"]
        self.Wc, self.Hc = x1 - x0, y1 - y0

    # mundo (cm) -> papel (mm) e -> pixel da planta
    def mm(self, x, y): return (self.PX + (self.xr - x) * self.k, self.PY + (self.yr - y) * self.k)
    def px(self, x, y): return ((self.xr - x) * self.s, (self.yr - y) * self.s)

    # ---------------- planta humanizada (raster) ----------------
    def _pinta(self, img, g, mat):
        for p in _polys(g):
            pts = [self.px(*c) for c in p.exterior.coords]
            u0, v0 = max(0, int(min(a for a, _ in pts)) - 1), max(0, int(min(b for _, b in pts)) - 1)
            u1, v1 = min(img.width, int(max(a for a, _ in pts)) + 2), min(img.height, int(max(b for _, b in pts)) + 2)
            if u1 <= u0 or v1 <= v0: continue
            mk = Image.new("L", (u1 - u0, v1 - v0), 0); d = ImageDraw.Draw(mk)
            d.polygon([(a - u0, b - v0) for a, b in pts], fill=255)
            for h in p.interiors: d.polygon([(a - u0, b - v0) for a, b in (self.px(*c) for c in h.coords)], fill=0)
            V, U = np.mgrid[v0:v1, u0:u1].astype(float)
            tex = Image.fromarray(np.clip(MAT[mat](U, V, self.s), 0, 255).astype(np.uint8), "RGB")
            img.paste(tex, (u0, v0), mk)

    def _arvore(self, d, g, esc=(76, 128, 62), cla=(156, 202, 114)):
        (cx, cy), r = self.px(*g.centroid.coords[0]), math.sqrt(g.area / math.pi) * self.s
        rng = np.random.default_rng(int(cx * 31 + cy)); cont = tuple(int(v * 0.78) for v in esc) + (255,)
        n = 9 if r > 60 else 7
        for a in np.linspace(0, 2 * math.pi, n + 1)[:-1] + rng.uniform(0, 0.6):
            bx, by, br = cx + math.cos(a) * r * 0.6, cy + math.sin(a) * r * 0.6, r * rng.uniform(0.36, 0.44)
            d.ellipse([bx - br, by - br, bx + br, by + br], fill=esc + (255,), outline=cont, width=2)
        for k in range(5):
            f = k / 4; rr = r * (0.62 - k * 0.11); o = -k * r * 0.05
            c = tuple(int(esc[i] + (cla[i] - esc[i]) * f) for i in range(3))
            d.ellipse([cx + o - rr, cy + o - rr, cx + o + rr, cy + o + rr], fill=c + (255,))
        for a in np.linspace(0, 2 * math.pi, 5)[:-1] + 0.4:            # brilhos, como no modelo
            bx, by, br = cx + math.cos(a) * r * 0.45, cy + math.sin(a) * r * 0.45, r * 0.16
            d.ellipse([bx - br, by - br, bx + br, by + br], fill=cla + (255,))

    def render(self):
        c, s = self.c, self.s
        img = Image.new("RGB", (int(self.Wc * s), int(self.Hc * s)), (255, 255, 255))
        for g, m in c["pisos_externos"]: self._pinta(img, g, m)
        self._pinta(img, c["soleiras"], "porc90")
        for nome, g in c["ambientes"].items(): self._pinta(img, g, c["piso_de"](nome))
        for g, st in c["pecas"]:
            if st == "box": self._pinta(img, g, "box")
        # sombras so do mobiliario e da vegetacao (como no modelo)
        sh = Image.new("L", img.size, 0); ds = ImageDraw.Draw(sh)
        for g, st in c["pecas"]:
            if st in SEM_SOMBRA or not isinstance(g, Polygon): continue
            ds.polygon([self.px(*q) for q in g.exterior.coords], fill=255 if st in ("arvore", "arbusto", "guardasol") else 200)
        sh = np.array(sh.filter(ImageFilter.GaussianBlur(9))).astype(float)
        dsl = int(1.2 * s * 4)                                              # ~0,5 mm de deslocamento no papel
        sh = np.roll(np.roll(sh, dsl, 0), dsl, 1)
        img = Image.fromarray((np.array(img).astype(float) * (1 - sh[..., None] / 255 * 0.3)).astype(np.uint8))
        d = ImageDraw.Draw(img, "RGBA")
        for g, st in c["pecas"]:
            if isinstance(g, LineString):
                cor, lw = ((140, 185, 210), 4) if st == "vidro_linha" else ((150, 130, 104), 2)
                d.line([self.px(*q) for q in g.coords], fill=cor + (255,), width=lw); continue
            pts = [self.px(*q) for q in g.exterior.coords]
            if st == "arvore": self._arvore(d, g)
            elif st == "arbusto": self._arvore(d, g, (84, 136, 66), (164, 206, 120))
            elif st == "vaso_planta":
                (cx, cy), r = self.px(*g.centroid.coords[0]), math.sqrt(g.area / math.pi) * s
                d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(196, 170, 140, 255), outline=(150, 124, 96, 255), width=2)
                self._arvore(d, g.buffer(-5), (80, 134, 66), (160, 204, 118))
            elif st == "guardasol":
                (cx, cy), r = self.px(*g.centroid.coords[0]), math.sqrt(g.area / math.pi) * s
                for i in range(8):
                    d.pieslice([cx - r, cy - r, cx + r, cy + r], i * 45, (i + 1) * 45,
                               fill=(244, 240, 230, 240) if i % 2 else (226, 218, 200, 240), outline=(190, 180, 160, 255))
                d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(120, 100, 80, 255))
            elif st == "queimador":
                d.ellipse([min(a for a, _ in pts), min(b for _, b in pts), max(a for a, _ in pts), max(b for _, b in pts)],
                          outline=(150, 150, 150, 255), width=2)
            elif st == "bancada":
                self._pinta(img, g, "travertino"); d.polygon(pts, outline=(186, 170, 142, 255), width=2)
            else:
                f, o = COR.get(st, ((210, 210, 210), (140, 140, 140)))
                d.polygon(pts, fill=(f + (255,)) if f else None, outline=(o + (255,)) if o else None, width=2 if o else 1)
        # paredes, muros, gradil, esquadrias, portas
        for g in _polys(c["paredes"]): d.polygon([self.px(*q) for q in g.exterior.coords], fill=(30, 30, 30, 255))
        for g in c.get("muros", []): d.polygon([self.px(*q) for q in g.exterior.coords], fill=(30, 30, 30, 255))
        for g in c.get("gradil", []):
            (a, b), (e, f) = self.px(g.bounds[2], g.bounds[3]), self.px(g.bounds[0], g.bounds[1])
            d.rectangle([a, b, e, f], outline=(80, 80, 80, 255), width=2)
            for v in np.arange(b, f, 3 * s): d.line([(a, v), (e, v)], fill=(110, 110, 110, 255), width=2)
        for geo, ori in c["janelas"].values():
            x0, y0, x1, y1 = geo.bounds; (a, b), (e, f) = self.px(x1, y1), self.px(x0, y0)
            d.rectangle([a, b, e, f], fill=(255, 255, 255, 255), outline=(120, 120, 120, 255), width=2)
            if ori == "h": d.rectangle([a, (b + f) / 2 - 2, e, (b + f) / 2 + 2], fill=(190, 218, 234, 255))
            else: d.rectangle([(a + e) / 2 - 2, b, (a + e) / 2 + 2, f], fill=(190, 218, 234, 255))
        for h, cc, o, wd in c["portas"]:
            ab = (h[0] + o[0] * wd, h[1] + o[1] * wd); n = (-o[1] * 2, o[0] * 2)
            folha = Polygon([h, ab, (ab[0] + n[0] * 1.5, ab[1] + n[1] * 1.5), (h[0] + n[0] * 1.5, h[1] + n[1] * 1.5)])
            d.polygon([self.px(*q) for q in folha.exterior.coords], fill=(255, 255, 255, 255), outline=(100, 100, 100, 255), width=2)
            d.line([self.px(h[0] + wd * (cc[0] * math.cos(a) + o[0] * math.sin(a)), h[1] + wd * (cc[1] * math.cos(a) + o[1] * math.sin(a)))
                    for a in [math.pi / 2 * i / 30 for i in range(31)]], fill=(150, 150, 150, 255), width=1)
        for g in c.get("correr", []):
            x0, y0, x1, y1 = g.bounds
            for yy, xa, xb in ((y0 + 4, x0, (x0 + x1) / 2 + 10), (y1 - 4, (x0 + x1) / 2 - 10, x1)):
                (a, b), (e, f) = self.px(xb, yy + 1.5), self.px(xa, yy - 1.5)
                d.rectangle([a, b, e, f], fill=(255, 255, 255, 255), outline=(100, 100, 100, 255), width=2)
        return img

    # ---------------- primitivas vetoriais ----------------
    def txt(self, pg, x, y, s, tam, negrito=False, cor=PRETO, alin="c", rot=0):
        # (x, y) em mm = centro (alin c), inicio (l) ou fim (r) da linha de base deslocada p/ centralizar na altura
        f = F_BOLD if negrito else F_REG; w = f.text_length(s, fontsize=tam) / MM
        if rot == 0:
            dx = {"c": -w / 2, "l": 0, "r": -w}[alin]
            pg.insert_text(((x + dx) * MM, (y + tam * 0.35 / MM) * MM), s, fontsize=tam, fontname="AB" if negrito else "AR", color=cor)
        else:                                                          # 90 graus: le de baixo p/ cima
            dy = {"c": w / 2, "l": 0, "r": w}[alin]
            pg.insert_text(((x + tam * 0.35 / MM) * MM, (y + dy) * MM), s, fontsize=tam, fontname="AB" if negrito else "AR", color=cor, rotate=90)

    def lin(self, pg, a, b, cor=PRETO, w=0.5, dashes=None):
        pg.draw_line(pymupdf.Point(a[0] * MM, a[1] * MM), pymupdf.Point(b[0] * MM, b[1] * MM), color=cor, width=w, dashes=dashes)

    def ret(self, pg, x0, y0, x1, y1, cor=PRETO, w=0.5, fill=None):
        pg.draw_rect(pymupdf.Rect(x0 * MM, y0 * MM, x1 * MM, y1 * MM), color=cor, width=w, fill=fill)

    def cota(self, pg, p0, p1, lado=1, tam=5.6, alt=False):
        # p0, p1 no mundo, ja sobre a linha de cota; lado: +1 texto acima/esquerda, -1 abaixo/direita
        a, b = self.mm(*p0), self.mm(*p1)
        self.lin(pg, a, b, VERM, 0.35)
        for q in (a, b): self.lin(pg, (q[0] - 0.6, q[1] + 0.6), (q[0] + 0.6, q[1] - 0.6), VERM, 0.5)
        L = math.hypot(b[0] - a[0], b[1] - a[1]); val = f"{math.hypot(p1[0] - p0[0], p1[1] - p0[1]) / 100:.2f}".replace(".", ",")
        w = F_REG.text_length(val, fontsize=tam) / MM; mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        fora = w + 0.6 > L; off = 1.4 + (2.4 if (fora and alt) else 0)
        if abs(b[1] - a[1]) < 1e-6:
            self.txt(pg, mx, my - lado * off, val, tam, cor=VERM)
        else:
            self.txt(pg, mx - lado * off, my, val, tam, cor=VERM, rot=90)

    def cadeia(self, pg, pontos, fixo, horizontal=True, lado=1):
        # cotas encadeadas: pontos ordenados ao longo do eixo; fixo = coordenada da linha (mundo)
        pts = sorted(set(round(v, 1) for v in pontos))
        for i, (u, v) in enumerate(zip(pts, pts[1:])):
            if v - u < 0.5: continue
            p0, p1 = ((u, fixo), (v, fixo)) if horizontal else ((fixo, u), (fixo, v))
            self.cota(pg, p0, p1, lado, alt=(i % 2 == 1))
        a, b = ((pts[0], fixo), (pts[-1], fixo)) if horizontal else ((fixo, pts[0]), (fixo, pts[-1]))
        return a, b

    # ---------------- blocos da folha ----------------
    def legenda(self, pg, x, y, itens, colunas=2, larg=105):
        self.txt(pg, x, y, self.c["conteudo"], 13, True, alin="l")
        self.txt(pg, x, y + 6, f"ESCALA 1:{self.c['escala']}", 8, alin="l")
        self.txt(pg, x, y + 15, "LEGENDA", 9, True, alin="l")
        por_col = math.ceil(len(itens) / colunas)
        for i, tipo in enumerate(itens):
            cx, cy = x + (i // por_col) * larg, y + 21 + (i % por_col) * 7
            r = (cx, cy - 2.2, cx + 14, cy + 2.2)
            if tipo == "parede": self.ret(pg, *r, cor=(0.4, 0.4, 0.4), w=0.4, fill=(0.12, 0.12, 0.12))
            elif tipo == "projecao": self.lin(pg, (r[0], cy), (r[2], cy), (0.45, 0.45, 0.45), 0.6, "[2 1.5] 0")
            elif tipo == "esquadria": self.ret(pg, r[0], cy - 0.7, r[2], cy + 0.7, cor=(0.5, 0.6, 0.68), w=0.3, fill=(0.78, 0.87, 0.93))
            else:
                n = int(14 * self.s / self.k), int(4.4 * self.s / self.k)        # amostra na mesma escala da planta
                V, U = np.mgrid[0:n[1], 0:n[0]].astype(float)
                im = Image.fromarray(np.clip(MAT[tipo](U, V, self.s), 0, 255).astype(np.uint8))
                if tipo == "pedrisco":
                    dd = ImageDraw.Draw(im); rr = n[1] * 0.38
                    for fx in (0.22, 0.75):
                        dd.ellipse([n[0] * fx - rr, n[1] / 2 - rr, n[0] * fx + rr, n[1] / 2 + rr], fill=(84, 136, 66), outline=(60, 100, 50))
                buf = io.BytesIO(); im.save(buf, "PNG")
                pg.insert_image(pymupdf.Rect(r[0] * MM, r[1] * MM, r[2] * MM, r[3] * MM), stream=buf.getvalue())
                self.ret(pg, *r, cor=(0.6, 0.6, 0.6), w=0.3)
            self.txt(pg, cx + 17, cy, LEGENDA_PADRAO[tipo], 6.5, alin="l")
        return y + 21 + por_col * 7

    def quadro_areas(self, pg, x, y, w, internas, externas, totais):
        h, hc = 4.3, 5.2
        self.ret(pg, x, y, x + w, y + 8); self.txt(pg, x + w / 2, y + 4, "QUADRO DE ÁREAS", 10, True)
        yy = y + 8
        def bloco(titulo, itens, yy):
            self.lin(pg, (x, yy + hc), (x + w, yy + hc), PRETO, 0.6)
            self.txt(pg, x + 2, yy + hc / 2, titulo, 6.5, True, alin="l")
            self.txt(pg, x + w / 2 - 2, yy + hc / 2, "ÁREA (m²)", 6.5, True, alin="r"); self.txt(pg, x + w - 2, yy + hc / 2, "ÁREA (m²)", 6.5, True, alin="r")
            yy += hc; n = math.ceil(len(itens) / 2)
            for i, (nome, a) in enumerate(itens):
                col, lin = divmod(i, n); cx = x + col * w / 2; cy = yy + lin * h
                self.txt(pg, cx + 2, cy + h / 2, nome, 6.3, alin="l"); self.txt(pg, cx + w / 2 - 2, cy + h / 2, f"{a:.2f}".replace(".", ","), 6.3, alin="r")
            for lin in range(1, n + 1): self.lin(pg, (x, yy + lin * h), (x + w, yy + lin * h), LINHA_TAB, 0.3)
            self.lin(pg, (x + w / 2, yy), (x + w / 2, yy + n * h), PRETO, 0.4)
            return yy + n * h
        yy = bloco("ÁREAS INTERNAS", internas, yy)
        yy = bloco("ÁREAS EXTERNAS", externas, yy)
        self.lin(pg, (x, yy), (x + w, yy), PRETO, 0.6)
        for nome, a in totais:
            self.txt(pg, x + 2, yy + hc / 2, nome, 6.5, True, alin="l"); self.txt(pg, x + w - 2, yy + hc / 2, f"{a:.2f} m²".replace(".", ","), 6.5, True, alin="r")
            yy += hc; self.lin(pg, (x, yy), (x + w, yy), LINHA_TAB, 0.3)
        self.ret(pg, x, y, x + w, yy)
        return yy

    def quadro_mobiliario(self, pg, x, y, w, linhas, nota):
        cols = [0, 0.27, 0.74, 0.90, 1.0]; X = [x + w * f for f in cols]; h, hc = 4.2, 5.2
        self.ret(pg, x, y, x + w, y + 8); self.txt(pg, x + w / 2, y + 4, "QUADRO DE MOBILIÁRIO", 10, True)
        yy = y + 8
        for i, t in enumerate(("AMBIENTE", "ITEM", "DIM. (cm)", "QTD.")):
            if i < 2: self.txt(pg, X[i] + 2, yy + hc / 2, t, 6.3, True, alin="l")
            else: self.txt(pg, (X[i] + X[i + 1]) / 2, yy + hc / 2, t, 6.3, True)
        yy += hc; self.lin(pg, (x, yy), (x + w, yy), PRETO, 0.6)
        i = 0
        while i < len(linhas):
            amb = linhas[i][0]; j = i
            while j < len(linhas) and linhas[j][0] == amb: j += 1
            y0 = yy
            for amb_, item, dim, q in linhas[i:j]:
                self.txt(pg, X[1] + 2, yy + h / 2, item, 6.1, alin="l")
                self.txt(pg, (X[2] + X[3]) / 2, yy + h / 2, dim, 6.1); self.txt(pg, (X[3] + X[4]) / 2, yy + h / 2, str(q), 6.1)
                yy += h; self.lin(pg, (X[1], yy), (x + w, yy), LINHA_TAB, 0.3)
            self.txt(pg, X[0] + 2, (y0 + yy) / 2, amb, 6.1, True, alin="l")
            self.lin(pg, (x, yy), (x + w, yy), (0.45, 0.45, 0.45), 0.4)
            i = j
        for xx in X[1:-1]: self.lin(pg, (xx, y + 8), (xx, yy), (0.45, 0.45, 0.45), 0.4)
        self.ret(pg, x, y, x + w, yy)
        self.txt(pg, x, yy + 3.5, nota, 5.6, cor=CINZA, alin="l")
        return yy

    def carimbo(self, pg, x0, y0, x1, y1, d):
        w = x1 - x0; self.ret(pg, x0, y0, x1, y1, w=0.8)
        rows = [y0, y0 + 30, y0 + 44, y0 + 58, y0 + 72, y0 + 86]
        self.txt(pg, x0 + w / 2, y0 + 13, d["titulo"], 20, True); self.txt(pg, x0 + w / 2, y0 + 23, d["subtitulo"], 9.5)
        for yy in rows[1:]: self.lin(pg, (x0, yy), (x1, yy), PRETO, 0.5)
        def campo(xa, xb, ya, rot, val, tam=9):
            self.txt(pg, xa + 1.8, ya + 2.6, rot, 5, cor=CINZA, alin="l")
            if val: self.txt(pg, (xa + xb) / 2, ya + 8.5, val, tam, True)
        xm = x0 + w / 2; t1, t2 = x0 + w / 3, x0 + 2 * w / 3
        self.lin(pg, (xm, rows[1]), (xm, rows[2]), PRETO, 0.5); campo(x0, xm, rows[1], "PROJETO", d["projeto"], 7.5); campo(xm, x1, rows[1], "CLIENTE", d["cliente"], 7.5)
        campo(x0, x1, rows[2], "CONTEÚDO", d["conteudo"])
        for xx in (t1, t2): self.lin(pg, (xx, rows[3]), (xx, rows[4]), PRETO, 0.5)
        campo(x0, t1, rows[3], "ESCALA", d["escala"]); campo(t1, t2, rows[3], "DATA", d["data"]); campo(t2, x1, rows[3], "FOLHA", d["folha"])
        self.lin(pg, (xm, rows[4]), (xm, rows[5]), PRETO, 0.5)
        campo(x0, xm, rows[4], "ÁREA ÚTIL INTERNA", d["area_util"]); campo(xm, x1, rows[4], "ÁREA CONSTRUÍDA (FECHADA)", d["area_construida"])
        self.txt(pg, x0 + 1.8, rows[5] + 4, "OBSERVAÇÕES:", 6.5, True, alin="l")
        for i, ob in enumerate(d["obs"]): self.txt(pg, x0 + 1.8, rows[5] + 8.5 + i * 4, f"{i + 1}. {ob}", 6.2, alin="l")

    # ---------------- folha completa ----------------
    def gera(self, saida_pdf, saida_png=None):
        c = self.c; img = self.render()
        if saida_png: img.save(saida_png, optimize=True)
        doc = pymupdf.open(); W, H = c["folha_mm"]
        pg = doc.new_page(width=W * MM, height=H * MM)
        pg.insert_font(fontname="AR", fontfile=ARIAL); pg.insert_font(fontname="AB", fontfile=ARIAL_B)
        self.ret(pg, 10, 10, W - 10, H - 10, w=0.9)
        buf = io.BytesIO(); img.save(buf, "JPEG", quality=92)
        pg.insert_image(pymupdf.Rect(self.PX * MM, self.PY * MM, (self.PX + self.Wc * self.k) * MM, (self.PY + self.Hc * self.k) * MM), stream=buf.getvalue())
        for g in c.get("projecao", []):                                       # projecao da cobertura (tracejada)
            q = [self.mm(*p) for p in g.exterior.coords]
            for a, b in zip(q, q[1:]): self.lin(pg, a, b, (0.35, 0.35, 0.35), 0.6, "[3 2] 0")
        for (rot, area, (x, y)) in c["rotulos"]:                              # nomes e areas
            mx, my = self.mm(x, y)
            self.txt(pg, mx, my - 1.6, rot, 7.6, True)
            if area is not None: self.txt(pg, mx, my + 1.9, f"{area:.2f} m²".replace(".", ","), 6.4, cor=(0.27, 0.27, 0.27))
        for nota, (x, y), tam in c.get("notas", []): self.txt(pg, *self.mm(x, y), nota, tam, cor=(0.3, 0.3, 0.3))
        c["cotas"](self, pg)
        c["blocos"](self, pg)
        doc.save(saida_pdf, garbage=4, deflate=True)
        return img
