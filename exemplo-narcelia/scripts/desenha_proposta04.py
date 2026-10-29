# Desenha a Proposta 04 no documento ativo (Narcelia - Proposta 04.dwg).
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pythoncom
from win32com.client import VARIANT
from shapely.ops import unary_union
import proposta04 as P, frontal as F, entrada as E, fundos2 as C, gcad as G

assert G.doc.Name == "Narcelia - Proposta 04.dwg", "documento ativo nao e a proposta: " + G.doc.Name
geoms = lambda g: [p for p in (list(g.geoms) if hasattr(g, "geoms") else [g]) if p.area > 20]
limpa = lambda g: g.buffer(-0.5, join_style="mitre").buffer(0.5, join_style="mitre")

W_e = P.paredes(P.EX_ROOMS, P.EX_OPEN, P.EX_WIN)
W_p = P.paredes(P.ROOMS, P.OPENINGS, P.WINDOWS)
MANTER, DEMOLIR, CONSTRUIR = W_e.intersection(W_p), limpa(W_e.difference(W_p)), limpa(W_p.difference(W_e))

G.clear()
for nome, cor in {"ARQ-PAREDE": 7, "PROP-DEMOLIR": 2, "PROP-CONSTRUIR": 1, "ARQ-PORTA": 3, "ARQ-JANELA": 4,
                  "ARQ-TEXTO": 2, "ARQ-EXTERNO": 9, "PROP-PISCINA": 140, "PROP-MOBILIARIO": 8, "PROP-NOTAS": 30}.items():
    G.ensure_layer(nome, cor)
try:
    G.doc.Linetypes.Load("DASHED", "gcadiso.lin")
except Exception:
    pass
try:
    G.doc.Layers.Item("PROP-DEMOLIR").Linetype = "DASHED"; G.doc.SetVariable("LTSCALE", 8)
except Exception as e:
    print("sem tracejado:", e)

def contorno(g):
    out = []
    for p in geoms(g):
        out.append(G.pline(list(p.exterior.coords)[:-1]))
        for h in p.interiors: out.append(G.pline(list(h.coords)[:-1]))
    return out

G.layer("ARQ-PAREDE"); contorno(MANTER)
G.app.ZoomExtents(); G.app.ZoomScaled(0.85, 1)
G.layer("PROP-DEMOLIR"); contorno(DEMOLIR)
G.layer("PROP-CONSTRUIR")
for pl in contorno(CONSTRUIR):
    try:
        h = G.ms.AddHatch(0, "ANSI31", True)
        h.AppendOuterLoop(VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_DISPATCH, [pl])); h.PatternScale = 4; h.Evaluate()
    except Exception as e:
        pass

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
for k in P.CORRER:                                                   # portas de correr: 2 folhas
    x0, y0, x1, y1 = P.OPENINGS[k].bounds
    G.line((x0, y0 + 5), ((x0 + x1)/2 + 10, y0 + 5)); G.line(((x0 + x1)/2 - 10, y1 - 5), (x1, y1 - 5))

G.layer("ARQ-EXTERNO")                                              # limites do lote
for a, b in [((C.X_FIM, -15), (E.X_RUA, -15)), ((C.X_FIM, F.Y_DIVISA), (E.X_RUA, F.Y_DIVISA)),
             ((C.X_FIM, -15), (C.X_FIM, F.Y_DIVISA)), ((E.X_RUA, -15), (E.X_RUA, F.Y_DIVISA))]:
    G.line(a, b)
G.layer("PROP-PISCINA")
for g in (P.PISCINA, P.PISCINA.buffer(-20, join_style="mitre"), P.DECK):
    G.pline(list(g.exterior.coords)[:-1])
G.ensure_layer("PROP-COBERTURA", 5)
try:
    G.doc.Layers.Item("PROP-COBERTURA").Linetype = "DASHED"
except Exception:
    pass
G.layer("PROP-COBERTURA"); G.pline(list(P.COBERTURA.exterior.coords)[:-1])
G.layer("PROP-MOBILIARIO")
for g in P.VAGAS + [P.BANCADA, P.ILHA] + P.CLARABOIAS + P.EXTRAS:
    G.pline(list(g.exterior.coords)[:-1])
G.line((P.ILHA.bounds[0], P.ILHA.bounds[1]), (P.ILHA.bounds[2], P.ILHA.bounds[3]))

G.layer("ARQ-TEXTO")
for nome, geo in P.ROOMS.items():
    p = geo.representative_point() if geo.geom_type != "Polygon" or len(geo.exterior.coords) > 5 else geo.centroid
    cx, cy = p.coords[0]
    G.ctext(nome, cx, cy + 12, 14); G.ctext(f"{geo.area/1e4:.2f} m2", cx, cy - 12, 10)
G.layer("PROP-NOTAS")
for txt, (x, y), h in P.NOTAS:
    G.ctext(txt, x, y, h)
G.ctext("PROPOSTA 04 - REVISAO DA 02 - CASA UNICA", -600, -260, 30)
G.ctext("ENTRADA NA FACHADA | JANTAR + COZINHA ATE O VIDRO | ESTAR + TV | 3 SUITES | GOURMET ABERTO + BANHO LAZER", -600, -370, 14)
G.ctext("LEGENDA:  BRANCO = MANTER   |   AMARELO TRACEJADO = DEMOLIR   |   VERMELHO HACHURADO = CONSTRUIR", -600, -320, 16)
G.app.ZoomExtents(); G.app.ZoomScaled(0.9, 1)
G.doc.Save()
area = sum(g.area for g in P.ROOMS.values()) / 1e4
print(f"ok {G.ms.Count} entidades | demolir {DEMOLIR.area/1e4:.2f} m2 de parede | construir {CONSTRUIR.area/1e4:.2f} m2 | area util {area:.1f} m2")
for nome, g in (("DEMOLIR", DEMOLIR), ("CONSTRUIR", CONSTRUIR)):
    for p in geoms(g): print("  ", nome, [round(v) for v in p.bounds])
