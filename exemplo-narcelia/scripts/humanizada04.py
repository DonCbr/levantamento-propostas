# Planta humanizada da Proposta 04 (PNG + PDF em 1:50). Uso: py humanizada04.py
# Mesma vista do CAD (rua a esquerda): u = rua - x, v = divisa do corredor - y.
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from shapely.geometry import Polygon, MultiPolygon, LineString
from shapely.ops import unary_union
import proposta04 as P, layout04 as Y

S = 2.0                                   # px por cm (PDF a 254 dpi = escala 1:50)
X_RUA, Y_TOPO = 1172, 997
M, TOP, BASE = 140, 150, 430
W = int(2 * M + (X_RUA - Y.LOTE.bounds[0]) * S); H = int(TOP + (Y_TOPO + 15) * S + BASE)
uv = lambda x, y: (M + (X_RUA - x) * S, TOP + (Y_TOPO - y) * S)
SAIDA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Narcelia - Proposta 04 - Planta Humanizada")

def fonte(tam, negrito=False):
    try:
        f = ImageFont.truetype("C:/Windows/Fonts/bahnschrift.ttf", tam)
        f.set_variation_by_name("Bold" if negrito else "Regular"); return f
    except Exception:
        return ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf" if negrito else "C:/Windows/Fonts/arial.ttf", tam)

# ---------------- texturas (coordenadas absolutas em px, continuas entre ambientes) ----------------
def h2(a, b, seed):
    x = (a.astype(np.int64) * 73856093) ^ (b.astype(np.int64) * 19349663) ^ (seed * 83492791)
    return (x % 10007) / 10007.0

def madeira(U, V, base, pw=40, comp=320, seed=1, vertical=False, var=0.14):
    if vertical: U, V = V, U
    row = V // pw; off = (h2(row, row * 0 + 7, seed) * comp).astype(np.int64); k = (U + off) // comp
    t = 1 + (h2(row, k, seed) - 0.5) * var
    t += 0.025 * np.sin((V % pw) * 0.9 + h2(row, k, seed + 1) * 20) + 0.012 * np.sin(U * 0.021 + row)
    junta = ((V % pw) == 0) | (((U + off) % comp) == 0)
    t = np.where(junta, 0.72, t)
    return np.clip(np.array(base)[None, None, :] * t[..., None], 0, 255)

def ladrilho(U, V, base, t=120, jit=0.05, rejunte=None, seed=2, esp=2):
    i, j = U // t, V // t
    c = np.array(base)[None, None, :] * (1 + (h2(i, j, seed) - 0.5) * jit)[..., None]
    r = np.array(rejunte or [v * 0.88 for v in base])
    junta = ((U % t) < esp) | ((V % t) < esp)
    return np.clip(np.where(junta[..., None], r, c), 0, 255)

def intertravado(U, V):
    row = V // 20; off = (row % 2) * 20; i = (U + off) // 40
    c = np.array([176, 164, 150])[None, None, :] * (1 + (h2(i, row, 5) - 0.5) * 0.2)[..., None]
    junta = ((V % 20) < 2) | (((U + off) % 40) < 2)
    return np.clip(np.where(junta[..., None], np.array([140, 132, 122]), c), 0, 255)

def grama(U, V):
    rng = np.random.default_rng(int(U[0, 0]) * 7 + int(V[0, 0]))
    t = 1 + rng.normal(0, 0.07, U.shape) + 0.06 * np.sin(U * 0.013) * np.sin(V * 0.017) + 0.04 * np.sin(U * 0.031 + V * 0.011)
    return np.clip(np.array([108, 150, 74])[None, None, :] * t[..., None], 0, 255)

def seixos(U, V):
    i, j = (U + (V // 9) * 4) // 9, V // 9
    t = 0.82 + h2(i, j, 9) * 0.3
    return np.clip(np.array([206, 200, 188])[None, None, :] * t[..., None], 0, 255)

def agua(U, V):
    t = (V - V.min()) / max(1, V.max() - V.min())
    c = np.array([96, 188, 218])[None, None, :] * (1 - t[..., None]) + np.array([44, 142, 194])[None, None, :] * t[..., None]
    k = np.sin(U * 0.06 + 3 * np.sin(V * 0.045)) * np.sin(V * 0.05 + 2 * np.sin(U * 0.035))
    return np.clip(c + (k > 0.72)[..., None] * 38, 0, 255)

def liso(cor): return lambda U, V: np.broadcast_to(np.array(cor, float), U.shape + (3,))

MAT = {
    "madeira": lambda U, V: madeira(U, V, [203, 168, 126]),
    "madeira_gourmet": lambda U, V: madeira(U, V, [176, 140, 104], pw=30, comp=360, seed=3),
    "deck": lambda U, V: madeira(U, V, [150, 106, 72], pw=28, comp=420, seed=4, vertical=True, var=0.2),
    "porcelanato": lambda U, V: ladrilho(U, V, [228, 224, 216], t=180, jit=0.04),
    "porcelanato_ext": lambda U, V: ladrilho(U, V, [207, 202, 191], t=120, jit=0.06),
    "banheiro": lambda U, V: ladrilho(U, V, [236, 235, 231], t=120, jit=0.03, rejunte=[208, 206, 200]),
    "box": lambda U, V: ladrilho(U, V, [205, 214, 214], t=20, jit=0.08, esp=1),
    "cimenticio": lambda U, V: ladrilho(U, V, [200, 198, 191], t=120, jit=0.07),
    "cimenticio_ext": lambda U, V: ladrilho(U, V, [188, 184, 176], t=80, jit=0.09),
    "pedra": lambda U, V: ladrilho(U, V, [192, 186, 174], t=60, jit=0.14, seed=6),
    "intertravado": intertravado, "grama": grama, "seixos": seixos, "agua": agua,
    "borda": liso([238, 234, 224]), "canteiro": liso([112, 90, 66]),
}
PISO = {"ESTAR (PE-DIREITO DUPLO)": "madeira", "SALA DE TV": "madeira", "CORREDOR 100": "madeira", "SUITE 1": "madeira",
        "SUITE 2": "madeira", "SUITE MASTER": "madeira", "CLOSET MASTER": "madeira", "JANTAR / COZINHA": "porcelanato",
        "JARDIM DE INVERNO": "seixos", "AREA DE SERVICO COBERTA": "cimenticio", "AREA DE SERVICO DESCOBERTA": "cimenticio_ext",
        "GOURMET": "madeira_gourmet"}

img = Image.new("RGB", (W, H), (250, 249, 246))
def polys(g):
    if g.is_empty: return []
    return [p for p in (g.geoms if hasattr(g, "geoms") else [g]) if isinstance(p, Polygon) and p.area > 1]

def pinta(g, mat):
    for p in polys(g):
        pts = [uv(*c) for c in p.exterior.coords]
        u0, v0 = int(min(a for a, _ in pts)) - 1, int(min(b for _, b in pts)) - 1
        u1, v1 = int(max(a for a, _ in pts)) + 2, int(max(b for _, b in pts)) + 2
        mk = Image.new("L", (u1 - u0, v1 - v0), 0); d = ImageDraw.Draw(mk)
        d.polygon([(a - u0, b - v0) for a, b in pts], fill=255)
        for h in p.interiors: d.polygon([(a - u0, b - v0) for a, b in (uv(*c) for c in h.coords)], fill=0)
        V, U = np.mgrid[v0:v1, u0:u1]
        tex = Image.fromarray(MAT[mat](U, V).astype(np.uint8), "RGB")
        img.paste(tex, (u0, v0), mk)

# ---------------- pisos ----------------
for g, m in Y.EXTERNOS: pinta(g, m)
aberto = unary_union([g.buffer(1) for k, g in P.OPENINGS.items() if "ABERTA" in k])   # faixa descoberta: sem soleira
pinta(unary_union(list(P.ROOMS.values())).buffer(P.T, join_style="mitre").difference(aberto), "madeira")   # soleiras dos vaos
for nome, g in P.ROOMS.items(): pinta(g, PISO.get(nome, "banheiro"))
for g, s in Y.PECAS:
    if s == "box": pinta(g, "box")

# ---------------- sombras (paredes, muros, mobiliario, arvores) ----------------
WALLS = unary_union([P.paredes(P.ROOMS, P.OPENINGS, P.WINDOWS)] + P.EXTRA)
sh = Image.new("L", (W, H), 0); ds = ImageDraw.Draw(sh)
SEM_SOMBRA = {"tapete", "box", "ralo", "linha", "vidro_linha", "pedra", "queimador", "loucas2", "inox", "inox_escuro", "vidro", "luminaria"}
for g in polys(WALLS) + [p for m in Y.MUROS for p in polys(m)]:
    ds.polygon([uv(*c) for c in g.exterior.coords], fill=255)
for g, s in Y.PECAS:
    if s in SEM_SOMBRA or not isinstance(g, Polygon): continue
    k = 255 if s in ("arvore", "guardasol") else 190
    ds.polygon([uv(*c) for c in g.exterior.coords], fill=k)
sh = sh.filter(ImageFilter.GaussianBlur(7))
sh = np.roll(np.roll(np.array(sh), 10, 0), 10, 1)                   # sombra deslocada p/ baixo e p/ a direita
arr = np.array(img).astype(float) * (1 - sh[..., None] / 255 * 0.36)
img = Image.fromarray(arr.astype(np.uint8))

# ---------------- mobiliario ----------------
COR = {  # estilo -> (preenchimento, contorno)
    "cama": ((247, 245, 240), (150, 148, 142)), "travesseiro": ((255, 255, 255), (170, 168, 160)),
    "lencol": ((214, 200, 178), (160, 146, 124)), "madeira": ((156, 117, 82), (104, 76, 52)),
    "mesa": ((150, 110, 76), (98, 70, 48)), "armario": ((222, 208, 188), (150, 132, 112)),
    "estofado2": ((118, 128, 138), (82, 90, 98)), "almofada": ((142, 152, 162), (100, 108, 116)),
    "almofada_clara": ((245, 244, 238), (175, 172, 165)), "tapete": ((226, 215, 194), None),
    "tv": ((30, 30, 32), None), "bancada": ((238, 236, 230), (160, 158, 152)),
    "inox": ((204, 208, 212), (140, 145, 150)), "inox_escuro": ((58, 58, 60), None),
    "loucas": ((255, 255, 255), (140, 140, 140)), "loucas2": ((228, 236, 240), (170, 175, 180)),
    "cadeira": ((122, 92, 66), (84, 62, 44)), "vidro": ((186, 216, 232), (120, 160, 185)),
    "carro": ((62, 84, 112), (36, 50, 70)), "carro2": ((50, 68, 92), (36, 50, 70)),
    "pedra": ((206, 200, 188), (160, 152, 140)), "luminaria": ((252, 242, 205), (200, 185, 140)),
    "box": (None, (150, 170, 178)), "ralo": ((120, 120, 120), None),
    "manta": ((176, 112, 84), (140, 88, 64)), "vidro_carro": ((40, 52, 66), None),
}
d = ImageDraw.Draw(img, "RGBA")

def arvore(g, cor_esc=(56, 102, 50), cor_cla=(128, 172, 86)):
    (cx, cy), r = uv(*g.centroid.coords[0]), math.sqrt(g.area / math.pi) * S
    rng = np.random.default_rng(int(cx * 31 + cy))
    for a in np.linspace(0, 2 * math.pi, 11)[:-1] + rng.uniform(0, 0.5):
        bx, by, br = cx + math.cos(a) * r * 0.62, cy + math.sin(a) * r * 0.62, r * rng.uniform(0.33, 0.42)
        d.ellipse([bx - br, by - br, bx + br, by + br], fill=cor_esc + (255,))
    for k in range(6):
        f = k / 5; rr = r * (0.78 - k * 0.11); o = -k * r * 0.05
        c = tuple(int(cor_esc[i] + (cor_cla[i] - cor_esc[i]) * f) for i in range(3))
        d.ellipse([cx + o - rr, cy + o - rr, cx + o + rr, cy + o + rr], fill=c + (255,))
    d.line([(cx - r * 0.25, cy), (cx + r * 0.25, cy)], fill=(70, 100, 55), width=2)
    d.line([(cx, cy - r * 0.25), (cx, cy + r * 0.25)], fill=(70, 100, 55), width=2)

for g, s in Y.PECAS:
    if isinstance(g, LineString):
        cor, lw = ((120, 170, 200), 4) if s == "vidro_linha" else ((110, 100, 90), 2)
        d.line([uv(*c) for c in g.coords], fill=cor + (255,), width=lw); continue
    pts = [uv(*c) for c in g.exterior.coords]
    if s == "arvore": arvore(g)
    elif s == "arbusto": arvore(g, (64, 112, 54), (140, 180, 92))
    elif s == "vaso_planta":
        (cx, cy), r = uv(*g.centroid.coords[0]), math.sqrt(g.area / math.pi) * S
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(176, 146, 116, 255), outline=(120, 96, 72, 255), width=2)
        arvore(g.buffer(-6), (60, 108, 52), (132, 176, 88))
    elif s == "guardasol":
        (cx, cy), r = uv(*g.centroid.coords[0]), math.sqrt(g.area / math.pi) * S
        for i in range(8):
            d.pieslice([cx - r, cy - r, cx + r, cy + r], i * 45, (i + 1) * 45, fill=((236, 230, 214, 235) if i % 2 else (214, 120, 84, 235)))
        d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(90, 70, 50, 255))
    elif s == "queimador":
        d.ellipse([min(a for a, _ in pts), min(b for _, b in pts), max(a for a, _ in pts), max(b for _, b in pts)], outline=(150, 150, 150, 255), width=2)
    else:
        f, o = COR.get(s, ((200, 200, 200), (120, 120, 120)))
        d.polygon(pts, fill=(f + (255,)) if f else None, outline=(o + (255,)) if o else None, width=2 if o else 1)

# ---------------- paredes, muros, esquadrias, portas ----------------
for g in polys(WALLS): d.polygon([uv(*c) for c in g.exterior.coords], fill=(46, 46, 46, 255))
for m in Y.MUROS: d.polygon([uv(*c) for c in m.exterior.coords], fill=(112, 112, 110, 255))
for m in Y.GRADIL:
    (a, b), (c, e) = uv(m.bounds[0], m.bounds[1]), uv(m.bounds[2], m.bounds[3])
    d.line([((a + c) / 2, e), ((a + c) / 2, b)], fill=(70, 70, 70, 255), width=3)
    for v in np.arange(e, b, 14): d.line([(c, v), (a, v)], fill=(90, 90, 90, 255), width=2)
for geo, ori in P.WINDOWS.values():
    x0, y0, x1, y1 = geo.bounds; (a, b), (c, e) = uv(x1, y1), uv(x0, y0)
    d.rectangle([a, b, c, e], fill=(250, 250, 250, 255), outline=(90, 130, 155, 255), width=2)
    if ori == "h": d.line([(a, (b + e) / 2), (c, (b + e) / 2)], fill=(90, 150, 185, 255), width=3)
    else: d.line([((a + c) / 2, b), ((a + c) / 2, e)], fill=(90, 150, 185, 255), width=3)
for h, c, o, wd in P.DOORS.values():
    d.line([uv(*h), uv(h[0] + o[0] * wd, h[1] + o[1] * wd)], fill=(60, 60, 60, 255), width=4)
    d.line([uv(h[0] + wd * (c[0] * math.cos(a) + o[0] * math.sin(a)), h[1] + wd * (c[1] * math.cos(a) + o[1] * math.sin(a)))
            for a in [math.pi / 2 * i / 24 for i in range(25)]], fill=(120, 120, 120, 255), width=2)
for k in P.CORRER:
    x0, y0, x1, y1 = P.OPENINGS[k].bounds
    d.line([uv(x0, y0 + 5), uv((x0 + x1) / 2 + 10, y0 + 5)], fill=(60, 60, 60, 255), width=3)
    d.line([uv((x0 + x1) / 2 - 10, y1 - 5), uv(x1, y1 - 5)], fill=(60, 60, 60, 255), width=3)

# ---------------- rotulos ----------------
FN, FA, FE = fonte(30, True), fonte(24), fonte(28, True)
for chave, (rot, (x, y)) in Y.NOMES.items():
    u, v = uv(x, y)
    d.text((u, v - 14), rot, font=FN, fill=(38, 38, 38, 255), anchor="mm", stroke_width=5, stroke_fill=(255, 255, 255, 235))
    d.text((u, v + 18), f"{P.ROOMS[chave].area / 1e4:.2f} m²".replace(".", ","), font=FA, fill=(70, 70, 70, 255),
           anchor="mm", stroke_width=4, stroke_fill=(255, 255, 255, 235))
for rot, (x, y) in Y.EXTERNOS_NOMES:
    d.text(uv(x, y), rot, font=FE, fill=(40, 52, 40, 255), anchor="mm", stroke_width=5, stroke_fill=(255, 255, 255, 230))
u, v = uv(530, 470)
d.text((u, v), "PÉ-DIREITO DUPLO", font=fonte(20), fill=(90, 90, 90, 255), anchor="mm", stroke_width=4, stroke_fill=(255, 255, 255, 230))

# ---------------- carimbo ----------------
y0 = TOP + (Y_TOPO + 15) * S + 70
d.line([(M, y0), (W - M, y0)], fill=(60, 60, 60, 255), width=3)
d.text((M, y0 + 40), "PROPOSTA 04 · PLANTA HUMANIZADA", font=fonte(64, True), fill=(30, 30, 30, 255))
d.text((M, y0 + 130), "Casa Narcelia · estudo preliminar · revisão da Proposta 02", font=fonte(36), fill=(80, 80, 80, 255))
area = sum(g.area for g in P.ROOMS.values()) / 1e4
d.text((M, y0 + 185), f"Área útil: {area:.0f} m² · 3 suítes · estar com pé-direito duplo · gourmet aberto para a piscina".replace(".", ","),
       font=fonte(30), fill=(80, 80, 80, 255))
ex = W - M - 1000                                            # escala grafica 0-5 m
for i in range(5):
    d.rectangle([ex + i * 200, y0 + 60, ex + (i + 1) * 200, y0 + 80], fill=((40, 40, 40, 255) if i % 2 == 0 else (250, 250, 250, 255)), outline=(40, 40, 40, 255), width=2)
    d.text((ex + i * 200, y0 + 92), f"{i}", font=fonte(26), fill=(60, 60, 60, 255), anchor="mt")
d.text((ex + 1000, y0 + 92), "5 m", font=fonte(26), fill=(60, 60, 60, 255), anchor="mt")
d.text((ex + 1000, y0 + 150), "PDF impresso em tamanho real: escala 1:50", font=fonte(26), fill=(100, 100, 100, 255), anchor="rt")

img.save(SAIDA + ".png", optimize=True)
img.save(SAIDA + ".pdf", resolution=254.0)
print("ok", W, "x", H, "->", SAIDA + ".png / .pdf")
