# Motor generico: desenha no GstarCAD aberto os modulos de um levantamento.
# Uso: py motor.py <pasta_do_projeto\scripts> modulo1 modulo2 ...
# Cada modulo (ex.: casa_frontal.py) define, no referencial da folha (cm, x p/ a rua, y p/ cima):
#   ROOMS {nome: retangulo}  OPENINGS {nome: retangulo}  WINDOWS {nome: (retangulo, "h"|"v")}
#   DOORS {nome: (dobradica, dir_fechada, dir_aberta, largura)}
#   opcionais: MERGE {ret_secundario: ret_principal}, LOUCAS [pontos], NOTES [(txt, (x,y), h)],
#              LINES [(camada, p1, p2)], EXTRA_WALL [retangulo]
import sys, os, math, importlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shapely.ops import unary_union
import gcad as G

T = 15
CAMADAS = {"ARQ-PAREDE": 7, "ARQ-PORTA": 3, "ARQ-JANELA": 4, "ARQ-COTA": 1, "ARQ-TEXTO": 2,
           "ARQ-LOUCA": 8, "ARQ-GRADE": 6, "ARQ-EXTERNO": 9, "ARQ-CONFERIR": 30}

def carregar(pasta, nomes):
    sys.path.insert(0, pasta)
    mods = [importlib.import_module(n) for n in nomes]
    junta = lambda attr, vazio: (
        {k: v for m in mods for k, v in getattr(m, attr, vazio).items()} if isinstance(vazio, dict)
        else [x for m in mods for x in getattr(m, attr, vazio)])
    return {a: junta(a, {}) for a in ("ROOMS", "OPENINGS", "WINDOWS", "DOORS", "MERGE")} | \
           {a: junta(a, []) for a in ("LOUCAS", "NOTES", "LINES", "EXTRA_WALL")}

def paredes(M):
    espacos = unary_union(list(M["ROOMS"].values()))
    pegada = unary_union([espacos.buffer(T, join_style="mitre")] + M["EXTRA_WALL"])
    vaos = unary_union([espacos] + list(M["OPENINGS"].values()) + [w for w, _ in M["WINDOWS"].values()])
    return pegada.difference(vaos)

def desenhar(M):
    G.clear()
    for nome, cor in CAMADAS.items(): G.ensure_layer(nome, cor)
    w = paredes(M)
    G.layer("ARQ-PAREDE")
    for p in (list(w.geoms) if hasattr(w, "geoms") else [w]):
        G.pline(list(p.exterior.coords)[:-1])
        for h in p.interiors: G.pline(list(h.coords)[:-1])
    G.app.ZoomExtents(); G.app.ZoomScaled(0.85, 1)
    G.layer("ARQ-PORTA")
    for h, c, o, wd in M["DOORS"].values():
        G.line(h, (h[0] + o[0]*wd, h[1] + o[1]*wd))
        G.pline([(h[0] + wd*(c[0]*math.cos(a) + o[0]*math.sin(a)), h[1] + wd*(c[1]*math.cos(a) + o[1]*math.sin(a)))
                 for a in [math.pi/2*i/16 for i in range(17)]], closed=False)
    G.layer("ARQ-JANELA")
    for geo, ori in M["WINDOWS"].values():
        x0, y0, x1, y1 = geo.bounds
        G.pline([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])
        for f in (1/3, 2/3):
            if ori == "h": y = y0 + (y1-y0)*f; G.line((x0, y), (x1, y))
            else:          x = x0 + (x1-x0)*f; G.line((x, y0), (x, y1))
    G.layer("ARQ-LOUCA")
    for pts in M["LOUCAS"]: G.pline(pts)
    for camada, a, b in M["LINES"]:
        G.layer(camada); G.line(a, b)
    G.layer("ARQ-TEXTO")
    for nome, geo in M["ROOMS"].items():
        if nome in M["MERGE"]: continue
        area = unary_union([geo] + [M["ROOMS"][k] for k, v in M["MERGE"].items() if v == nome]).area
        cx, cy = geo.centroid.coords[0]
        G.ctext(nome, cx, cy + 10, 15); G.ctext(f"{area/1e4:.2f} m2", cx, cy - 14, 10)
    for nome, (geo, ori) in M["WINDOWS"].items():
        if nome.startswith("J "):
            cx, cy = geo.centroid.coords[0]
            G.ctext(nome.split(" ")[1], cx + (40 if ori == "v" else 0), cy + (30 if ori == "h" else 0), 9)
    for txt, (x, y), h in M["NOTES"]:
        G.layer("ARQ-CONFERIR" if "CONFERIR" in txt else "ARQ-TEXTO"); G.ctext(txt, x, y, h)
    G.app.ZoomExtents(); G.app.ZoomScaled(0.9, 1)
    print("desenhado:", G.ms.Count, "entidades")

if __name__ == "__main__":
    desenhar(carregar(sys.argv[1], sys.argv[2:]))
