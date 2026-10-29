# Desenha a planta de layout da Proposta 04 no documento ativo (Narcelia - Proposta 04 - Layout.dwg).
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pythoncom
from win32com.client import VARIANT
from shapely.geometry import Polygon, LineString
from shapely.ops import unary_union
import proposta04 as P, layout04 as Y, gcad as G

assert G.doc.Name == "Narcelia - Proposta 04 - Layout.dwg", "documento ativo nao e o layout: " + G.doc.Name
G.PAUSA = 0.03
geoms = lambda g: [p for p in (list(g.geoms) if hasattr(g, "geoms") else [g]) if p.area > 1]
disp = lambda pls: VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_DISPATCH, pls)

G.clear()
for nome, cor in {"ARQ-PAREDE": 7, "ARQ-PAREDE-HACHURA": 8, "ARQ-PORTA": 3, "ARQ-JANELA": 4, "ARQ-TEXTO": 2, "ARQ-EXTERNO": 9,
                  "LAY-MOBILIARIO": 30, "LAY-LOUCAS": 4, "LAY-VEGETACAO": 3, "LAY-PISCINA": 140, "LAY-PISO-EXTERNO": 8,
                  "PROP-NOTAS": 30}.items():
    G.ensure_layer(nome, cor)
CAMADA = {"loucas": "LAY-LOUCAS", "loucas2": "LAY-LOUCAS", "box": "LAY-LOUCAS", "ralo": "LAY-LOUCAS", "vidro_linha": "LAY-LOUCAS",
          "arvore": "LAY-VEGETACAO", "arbusto": "LAY-VEGETACAO", "vaso_planta": "LAY-VEGETACAO", "pedra": "LAY-PISO-EXTERNO"}

# paredes com hachura solida
W = unary_union([P.paredes(P.ROOMS, P.OPENINGS, P.WINDOWS)] + P.EXTRA)
for p in geoms(W):
    G.layer("ARQ-PAREDE")
    ext = G.pline(list(p.exterior.coords)[:-1]); ints = [G.pline(list(h.coords)[:-1]) for h in p.interiors]
    G.layer("ARQ-PAREDE-HACHURA")
    try:
        h = G.ms.AddHatch(0, "SOLID", True); h.AppendOuterLoop(disp([ext]))
        for i in ints: h.AppendInnerLoop(disp([i]))
        h.Evaluate()
    except Exception as e:
        print("hachura:", e)
G.app.ZoomExtents(); G.app.ZoomScaled(0.85, 1)

# portas, esquadrias, portas de correr (mesmo desenho da proposta)
G.layer("ARQ-PORTA")
for h, c, o, wd in P.DOORS.values():
    G.line(h, (h[0] + o[0]*wd, h[1] + o[1]*wd))
    G.pline([(h[0] + wd*(c[0]*math.cos(a) + o[0]*math.sin(a)), h[1] + wd*(c[1]*math.cos(a) + o[1]*math.sin(a)))
             for a in [math.pi/2*i/16 for i in range(17)]], closed=False)
G.layer("ARQ-JANELA")
for geo, ori in P.WINDOWS.values():
    x0, y0, x1, y1 = geo.bounds
    G.pline([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])
    for f in (1/3, 2/3):
        if ori == "h": y = y0 + (y1-y0)*f; G.line((x0, y), (x1, y))
        else:          x = x0 + (x1-x0)*f; G.line((x, y0), (x, y1))
for k in P.CORRER:
    x0, y0, x1, y1 = P.OPENINGS[k].bounds
    G.line((x0, y0 + 5), ((x0 + x1)/2 + 10, y0 + 5)); G.line(((x0 + x1)/2 - 10, y1 - 5), (x1, y1 - 5))

# lote, muros, gradil e areas externas
G.layer("ARQ-EXTERNO")
G.pline(list(Y.LOTE.exterior.coords)[:-1])
for g in Y.MUROS + Y.GRADIL: G.pline(list(g.exterior.coords)[:-1])
for g, m in Y.EXTERNOS[1:]:
    G.layer("LAY-PISCINA" if m in ("agua", "borda") else "LAY-PISO-EXTERNO")
    G.pline(list(g.exterior.coords)[:-1])

# mobiliario, loucas e vegetacao
for g, s in Y.PECAS:
    G.layer(CAMADA.get(s, "LAY-MOBILIARIO"))
    if isinstance(g, LineString): G.pline(list(g.coords), closed=False)
    elif s in ("arvore", "arbusto", "vaso_planta", "guardasol"):
        (cx, cy), r = g.centroid.coords[0], math.sqrt(g.area / math.pi)
        X, Yc = G.cad(cx, cy); G.show(G.ms.AddCircle(G.arr([X, Yc, 0]), r))
        if s == "arvore": G.show(G.ms.AddCircle(G.arr([X, Yc, 0]), r * 0.15))
    else: G.pline(list(g.exterior.coords)[:-1])

# nomes e areas
G.layer("ARQ-TEXTO")
for chave, (rot, (x, y)) in Y.NOMES.items():
    G.ctext(chave.replace(" (PE-DIREITO DUPLO)", ""), x, y + 10, 14); G.ctext(f"{P.ROOMS[chave].area/1e4:.2f} m2", x, y - 12, 10)
G.layer("PROP-NOTAS")
for rot, (x, y) in Y.EXTERNOS_NOMES:
    G.ctext(rot.replace("×", "x").replace("Ç", "C").replace("Ã", "A"), x, y, 12)
G.ctext("PE-DIREITO DUPLO", 530, 470, 9)
G.ctext("PROPOSTA 04 - PLANTA DE LAYOUT - CASA UNICA", -600, -260, 30)
G.ctext("ESTAR + TV | JANTAR + COZINHA | 3 SUITES | GOURMET ABERTO + PISCINA | MOBILIARIO INDICATIVO", -600, -320, 14)
G.app.ZoomExtents(); G.app.ZoomScaled(0.9, 1)
G.doc.Save()
print(f"ok {G.ms.Count} entidades | {len(Y.PECAS)} pecas de layout")
