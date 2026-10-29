# Analise de consistencia do levantamento (sem desenhar).
# Uso: py analise.py <pasta_do_projeto\scripts> modulo1 modulo2 ...
import sys, os, math, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shapely.geometry import Polygon
from shapely.ops import unary_union
import motor

M = motor.carregar(sys.argv[1], sys.argv[2:])
R, W = M["ROOMS"], motor.paredes(M)
geoms = lambda g: list(g.geoms) if hasattr(g, "geoms") else [g]
uniao = lambda n: unary_union([R[n]] + [R[k] for k, v in M["MERGE"].items() if v == n])

print("== Paredes > 17 cm (trechos longos; cantos sao ignorados)")
for p in geoms(W.buffer(-8.6).buffer(8.6)):
    x0, y0, x1, y1 = p.bounds
    if max(x1 - x0, y1 - y0) > 40: print("  ", [round(v) for v in p.bounds])
print("== Comodos sobrepostos")
for (a, ga), (b, gb) in itertools.combinations(R.items(), 2):
    if ga.intersection(gb).area > 1: print("  ", a, "x", b)
print("== Portas: varredura batendo em parede / outras portas")
sw = {}
for k, (h, c, o, w) in M["DOORS"].items():
    sw[k] = Polygon([h] + [(h[0] + w*(c[0]*math.cos(a) + o[0]*math.sin(a)), h[1] + w*(c[1]*math.cos(a) + o[1]*math.sin(a)))
                           for a in [math.pi/2*i/16 for i in range(17)]])
    if sw[k].buffer(-1).intersection(W).area > 5: print("  ", k, "bate em parede")
for a, b in itertools.combinations(sw, 2):
    if sw[a].intersection(sw[b]).area > 5: print("   conflito:", a, "x", b)
print("== Unidades (comodos ligados por porta/vao) e acessos externos")
lig = {n: set() for n in R}
for n, g in M["MERGE"].items(): lig[n].add(g); lig[g].add(n)
for (a, ga), (b, gb) in itertools.combinations(R.items(), 2):
    if ga.distance(gb) < 0.5 and ga.intersection(gb).length > 20: lig[a].add(b); lig[b].add(a)
ext = {}
for k, g in M["OPENINGS"].items():
    perto = [n for n, rg in R.items() if rg.distance(g) < 1]
    for a, b in itertools.combinations(perto, 2): lig[a].add(b); lig[b].add(a)
    if len(perto) == 1: ext.setdefault(perto[0], []).append(k)
vistos = set()
for n in R:
    if n in vistos: continue
    pilha, comp = [n], set()
    while pilha:
        x = pilha.pop()
        if x not in comp: comp.add(x); pilha += list(lig[x])
    vistos |= comp
    ac = sorted({o for m in comp for o in ext.get(m, [])})
    tem_bwc = any("BANHEIRO" in m for m in comp)
    print("  -", sorted(comp - set(M["MERGE"])), "| acessos:", ac or "NENHUM", "" if tem_bwc else "| SEM BANHEIRO")
print("== Comodos sem janela")
for n in R:
    if n in M["MERGE"]: continue
    g = uniao(n).buffer(T := motor.T + 1)
    if not any(g.intersects(w) for w, _ in M["WINDOWS"].values()) and "CIRCULA" not in n and "CORREDOR" not in n:
        print("  ", n)
print("== Areas")
tot = 0
for n in R:
    if n in M["MERGE"]: continue
    tot += uniao(n).area / 1e4
print(f"   area util total: {tot:.1f} m2")
