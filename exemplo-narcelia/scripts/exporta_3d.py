# Exporta a geometria do existente e das propostas para o 3D web (JSON em cm, referencial da folha).
# Uso: py exporta_3d.py <saida.json>
import sys, os, re, json, importlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shapely.geometry import box
from shapely.ops import unary_union
import frontal as F, entrada as E, fundos2 as C

H, HH = 280, 560          # pe-direito normal e duplo
geoms = lambda g: [p for p in (list(g.geoms) if hasattr(g, "geoms") else [g]) if p.area > 5]
rings = lambda p: [[[round(x, 1), round(y, 1)] for x, y in p.exterior.coords[:-1]]] + \
                  [[[round(x, 1), round(y, 1)] for x, y in h.coords[:-1]] for h in p.interiors]

def tipo(nome):
    n = nome.upper()
    if any(k in n for k in ("BANH", "LAVABO", "BANHO")): return "molhado"
    if any(k in n for k in ("FAIXA", "POCO", "JARDIM", "DESCOBERTA", "SERVICO EXTERNO")): return "externo"
    if any(k in n for k in ("SUITE", "QUARTO", "CLOSET")): return "intimo"
    if "GOURMET" in n: return "lazer"
    if any(k in n for k in ("COZINHA", "SERVICO", "DESPENSA", "LAVANDERIA")): return "servico"
    if any(k in n for k in ("CORREDOR", "CIRCULA", "HALL")): return "circulacao"
    if any(k in n for k in ("ESTAR", "SALA", "JANTAR", "TV", "THEATER", "ESCRITORIO")): return "social"
    return "neutro"

def janela(nome):
    m = re.search(r"(\d+)x(\d+)/(\d+)", nome)
    if m: return int(m.group(3)), int(m.group(3)) + int(m.group(2))
    n = nome.upper()
    if "BANCADA" in n: return 100, 210
    if "ESQUADRIA" in n: return 0, 500
    if any(k in n for k in ("PANO", "VIDRO", "PORTA DE VIDRO")): return 0, 250
    return 100, 220

def cenario(nome, rooms, opens, wins, walls, alto=None, extras=None):
    alto_b = alto.buffer(1) if alto is not None else None
    W = []
    for p in geoms(walls):
        if alto_b is not None and p.intersects(alto_b):
            for a in geoms(p.intersection(alto_b)): W.append({"r": rings(a), "h": HH})
            for b in geoms(p.difference(alto_b)): W.append({"r": rings(b), "h": H})
        else:
            W.append({"r": rings(p), "h": H})
    hz = lambda g: HH if (alto_b is not None and g.intersects(alto_b)) else H
    J = []
    for k, (g, ori) in wins.items():
        s, t = janela(k); hh = hz(g)
        if t >= 500: t = hh - 20
        J.append({"b": [round(v, 1) for v in g.bounds], "s": s, "t": min(t, hh), "h": hh})
    V = []
    for k, g in opens.items():
        if any(w in k.upper() for w in ("ABERTA", "ABERTO")): continue
        V.append({"b": [round(v, 1) for v in g.bounds], "f": 230 if "CORRER" in k or "ENTRADA" in k else 210, "h": hz(g)})
    R = []
    for k, g in rooms.items():
        for p in geoms(g):
            R.append({"r": rings(p), "n": k, "k": tipo(k), "a": round(g.area / 1e4, 2)})
    return {"nome": nome, "paredes": W, "janelas": J, "vergas": V, "pisos": R, "extras": extras or {}}

def bx(g): return [round(v, 1) for v in g.bounds]

# ---------- mobiliario (layoutNN.py): cada peca vira um volume (cota de base e topo em cm) ----------
ALT = {"cama": (0, 45), "lencol": (0, 50), "manta": (0, 52), "travesseiro": (0, 57), "mesa": (0, 76), "cadeira": (0, 45),
       "armario": (0, 220), "almofada": (0, 45), "almofada_clara": (0, 36), "tapete": (0, 1.5), "tv": (50, 115),
       "bancada": (0, 90), "inox_escuro": (0, 91.5), "carro": (0, 105), "vidro_carro": (0, 125), "carro2": (0, 142),
       "pedra": (0, 3), "luminaria": (0, 62)}
VEG = ("arvore", "arbusto", "vaso_planta", "guardasol")

def altura(g, s, almof):
    x0, y0, x1, y1 = g.bounds; a = g.area / 1e4
    if s == "madeira": return (0, 110) if min(x1 - x0, y1 - y0) <= 10 else (0, 30) if a > 1 else (0, 55) if a < 0.25 else (0, 45)
    if s == "estofado2": return (0, 78) if g.intersects(almof) else (0, 45)        # sofa: encosto e bracos; sem almofada = banco/puff
    if s == "inox": return (0, 190) if a > 0.4 else (0, 85) if a > 0.3 else (0, 91)
    if s == "loucas": return (0, 85) if a > 0.3 else (0, 42)
    return ALT.get(s)

def moveis(Y):
    from prancha import COR
    almof = unary_union([g for g, s in Y.PECAS if s == "almofada"])
    hexa = lambda c: (c[0] << 16) | (c[1] << 8) | c[2]
    out, arv = [], []
    for g, s in Y.PECAS:
        if s in VEG:
            arv.append([round(g.centroid.x, 1), round(g.centroid.y, 1), round((g.area / 3.1416) ** 0.5, 1), s]); continue
        if s == "vidro_linha":
            out.append({"r": rings(g.buffer(1, cap_style=2)), "z0": 0, "z1": 200, "c": 0xbfdbe8, "v": 1}); continue
        if g.geom_type == "LineString": continue
        z = altura(g, s, almof)
        if z is None: continue
        if s == "estofado2" and g.intersects(almof): g = g.difference(almof)
        cor = (233, 221, 197) if s == "bancada" else (COR.get(s, ((200, 200, 200), None))[0] or (200, 200, 200))
        for p in geoms(g): out.append({"r": rings(p), "z0": z[0], "z1": z[1], "c": hexa(cor)})
    return out, arv

# ---------- existente ----------
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "desenha_tudo.py"), encoding="utf-8").read()
ns = {"__file__": "x"}; exec(src.split("G.clear()")[0].replace("gcad as G", "frontal as G"), ns)
cen = [cenario("Existente", ns["ROOMS"], ns["OPENINGS"], ns["WINDOWS"], ns["walls"](),
               extras={"grades": [bx(F.GRADE)], "tanques": []})]

# ---------- propostas ----------
# volume com pe-direito duplo: P01 = estar (sala + sacada); P02/P03/P04 = estar no antigo quarto 2
altos = {"proposta": box(-33, -15, 687, 293), "proposta02": box(372, 278, 687, 707), "proposta03": box(372, 278, 687, 707),
         "proposta04": box(372, 278, 687, 707)}
for mod, rot in (("proposta", "Proposta 01"), ("proposta02", "Proposta 02"), ("proposta03", "Proposta 03"), ("proposta04", "Proposta 04")):
    P = importlib.import_module(mod)
    W = P.paredes(P.ROOMS, P.OPENINGS, P.WINDOWS)
    ex = {"piscina": bx(P.PISCINA), "deck": bx(P.DECK), "vagas": [bx(v) for v in P.VAGAS],
          "bancadas": [bx(P.BANCADA), bx(P.ILHA)] + [bx(g) for g in getattr(P, "EXTRAS", [])],
          "claraboias": [bx(g) for g in getattr(P, "CLARABOIAS", [])]}
    if hasattr(P, "COBERTURA"): ex["cobertura"] = bx(P.COBERTURA)
    lay = "layout" + mod.replace("proposta", "")
    if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), lay + ".py")):   # proposta com layout
        Yl = importlib.import_module(lay)
        ex["moveis"], ex["arvores"] = moveis(Yl); ex["bancadas"] = []
        ex["itens"] = getattr(Yl, "ITENS3D", [])                       # modelos reais (catalogo da pagina)
        pr_mod = "prancha" + mod.replace("proposta", "")               # materiais de piso no padrao da prancha
        if ex["itens"] and os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), pr_mod + ".py")):
            PRc = importlib.import_module(pr_mod)
            ex["externos"] = [{"r": rings(p), "m": mt} for g, mt in PRc.CFG["pisos_externos"] for p in geoms(g)]
            ex["piso_m"] = {nome: PRc.piso_de(nome) for nome in P.ROOMS}
    cen.append(cenario(rot, P.ROOMS, P.OPENINGS, P.WINDOWS, W, alto=altos[mod], extras=ex))

lote = {"x0": C.X_FIM, "x1": E.X_RUA, "y0": -15, "y1": F.Y_DIVISA}
json.dump({"lote": lote, "cenarios": cen}, open(sys.argv[1], "w", encoding="utf-8"), separators=(",", ":"))
for c in cen:
    print(c["nome"], "paredes", len(c["paredes"]), "janelas", len(c["janelas"]), "vergas", len(c["vergas"]), "pisos", len(c["pisos"]))
print("bytes", os.path.getsize(sys.argv[1]))
