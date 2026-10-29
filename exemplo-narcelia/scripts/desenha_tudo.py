# Redesenha Casa Frontal + Entrada + Fundos 1 com as paredes calculadas em conjunto.
import sys, math, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shapely.ops import unary_union
import frontal as F, fundos1 as B, fundos2 as C, fundos3 as D, gcad as G

ROOMS = {**F.ROOMS, **B.ROOMS, **C.ROOMS, **D.ROOMS}
OPENINGS = {**F.OPENINGS, **B.OPENINGS, **C.OPENINGS, **D.OPENINGS}
WINDOWS = {**F.WINDOWS, **B.WINDOWS, **C.WINDOWS, **D.WINDOWS}
DOORS = {**F.DOORS, **B.DOORS, **C.DOORS, **D.DOORS}
MERGE = {**B.MERGE, **C.MERGE, **D.MERGE}

def walls():
    spaces = unary_union(list(ROOMS.values()))
    foot = unary_union([spaces.buffer(F.T, join_style="mitre"),
                        F.r(F.X_VIDRO, -F.T, F.SAC + F.T, F.T)])
    cut = unary_union([spaces] + list(OPENINGS.values()) + [w for w, _ in WINDOWS.values()])
    return foot.difference(cut)

G.clear()
G.ensure_layer("ARQ-GRADE", 6); G.ensure_layer("ARQ-EXTERNO", 9)

w = walls()
G.layer("ARQ-PAREDE")
for p in (list(w.geoms) if hasattr(w, "geoms") else [w]):
    G.pline(list(p.exterior.coords)[:-1])
    for h in p.interiors: G.pline(list(h.coords)[:-1])
G.app.ZoomExtents(); G.app.ZoomScaled(0.8, 1)

G.layer("ARQ-PORTA")
for nome, (h, c, o, wd) in DOORS.items():
    hx, hy = h
    G.line(h, (hx + o[0]*wd, hy + o[1]*wd))
    G.pline([(hx + wd*(c[0]*math.cos(a) + o[0]*math.sin(a)),
              hy + wd*(c[1]*math.cos(a) + o[1]*math.sin(a)))
             for a in [math.pi/2*i/16 for i in range(17)]], closed=False)

G.layer("ARQ-JANELA")
for nome, (geo, ori) in WINDOWS.items():
    x0, y0, x1, y1 = geo.bounds
    G.pline([(x0,y0),(x1,y0),(x1,y1),(x0,y1)])
    for f in (1/3, 2/3):
        if ori == "h": y = y0+(y1-y0)*f; G.line((x0,y),(x1,y))
        else:          x = x0+(x1-x0)*f; G.line((x,y0),(x,y1))

G.layer("ARQ-GRADE")
x0, y0, x1, y1 = F.GRADE.bounds
G.pline([(x0,y0),(x1,y0),(x1,y1),(x0,y1)])
for k in range(1, 12):
    y = y0 + (y1-y0)*k/12; G.line((x0-6,y),(x1+6,y))

G.layer("ARQ-EXTERNO")
x0, y0, x1, y1 = F.CAIXA.bounds
G.pline([(x0,y0),(x1,y0),(x1,y1),(x0,y1)]); G.line((x0,y0),(x1,y1)); G.line((x0,y1),(x1,y0))
G.line((C.X_FIM, F.Y_DIVISA), (687 + 60, F.Y_DIVISA))
G.line((C.X_FIM, C.PROF + 15), (C.X_FIM, D.Y_K0 - 15))   # divisa do fundo no corredor de 155   # divisa do corredor lateral

G.layer("ARQ-EXTERNO")
G.line((B.X_COL, B.Y_DEG), (B.X_COL - B.L_COL, B.Y_DEG))   # degrau quarto x patamar

G.layer("ARQ-LOUCA")
for pts in C.LOUCAS + D.LOUCAS:
    G.pline(pts)

G.layer("ARQ-TEXTO")
for nome, geo in ROOMS.items():
    if nome in MERGE: continue
    area = unary_union([geo] + [ROOMS[k] for k, v in MERGE.items() if v == nome]).area
    cx, cy = geo.centroid.coords[0]
    G.ctext(nome, cx, cy + 10, 15)
    G.ctext(f"{area/1e4:.2f} m2", cx, cy - 14, 10)
cx, cy = F.SACADA.centroid.coords[0]; G.ctext("SACADA", cx, cy, 12)
G.ctext("GRADE C/ ACESSO", F.GRADE.bounds[2] + 60, 139, 9)
G.ctext("PORTA DE VIDRO", F.X_VIDRO + 7, -40, 10)
G.ctext("CAIXA DE LUZ", 613, F.Y_BOT + 60, 9)
G.ctext("CORREDOR LATERAL", 150, F.Y_BOT + 15 + 145, 16)
for nome, (geo, ori) in WINDOWS.items():
    if nome.startswith("J "):
        cx, cy = geo.centroid.coords[0]
        G.ctext(nome.split(" ")[1], cx + (40 if ori == "v" else 0), cy + (30 if ori == "h" else 0), 9)
G.ctext("BANCADA 200x100", -725, 250, 8)
for txt, (x, y), h in B.NOTES + C.NOTES + D.NOTES:
    G.ctext(txt, x, y, h)

G.layer("ARQ-COTA")
G.dim((250, F.Y_BOT + 15), (250, F.Y_DIVISA), (290, F.Y_BOT + 15))

# --- cotas internas de cada ambiente (largura e comprimento) ---
import entrada as E
H = 10
for nome, geo in ROOMS.items():
    x0, y0, x1, y1 = geo.bounds
    if x1 - x0 >= 40: G.dim((x0, y0 + 22), (x1, y0 + 22), (x0, y0 + 22), H)
    if y1 - y0 >= 40: G.dim((x1 - 22, y0), (x1 - 22, y1), (x1 - 22, y0), H)

# --- correntes externas: divisa do fundo e lado do corredor lateral ---
def corrente(xs, y):
    xs = sorted(set(round(v, 1) for v in xs))
    for xa, xb in zip(xs, xs[1:]):
        if xb - xa >= 5: G.dim((xa, y), (xb, y), (xa, y), H)
na_divisa = [g for g in ROOMS.values() if abs(g.bounds[1]) < 0.5]
corrente([v for g in na_divisa for v in (g.bounds[0], g.bounds[2])] + [C.X_FIM, F.GRADE.bounds[2], E.X_RUA], -15 - 50)
no_corredor = [g for g in ROOMS.values() if abs(g.bounds[3] - F.Y_BOT) < 0.5]
corrente([v for g in no_corredor for v in (g.bounds[0], g.bounds[2])] + [B.X_COL - B.L_COL - 15, 672 + 15], F.Y_BOT + 15 + 45)

# --- cotas gerais do lote ---
G.dim((C.X_FIM, -15 - 110), (E.X_RUA, -15 - 110), (C.X_FIM, -15 - 110), 14)
G.dim((C.X_FIM - 60, -15), (C.X_FIM - 60, F.Y_DIVISA), (C.X_FIM - 60, -15), 14)
print("ok", G.ms.Count, "entidades")
