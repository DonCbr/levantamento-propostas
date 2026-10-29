# Proposta 01 - estudo preliminar (casa unica para venda).
# Usa o levantamento (frontal, fundos1, fundos2, fundos3) como existente e calcula
# MANTER / DEMOLIR / CONSTRUIR comparando as paredes existentes com as propostas.
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shapely.geometry import box
from shapely.ops import unary_union
import frontal as F, fundos1 as B, fundos2 as C, fundos3 as D, entrada as E

T = 15
r = lambda x0, y0, w, h: box(x0, y0, x0 + w, y0 + h)
U = lambda *g: unary_union(list(g))

# ---------------- EXISTENTE ----------------
EX_ROOMS = {**F.ROOMS, **B.ROOMS, **C.ROOMS, **D.ROOMS}
EX_OPEN = {**F.OPENINGS, **B.OPENINGS, **C.OPENINGS, **D.OPENINGS}
EX_WIN = {**F.WINDOWS, **B.WINDOWS, **C.WINDOWS, **D.WINDOWS}
EXTRA = [F.r(F.X_VIDRO, -T, F.SAC + T, T)]          # muro sobre a antiga sacada

def paredes(rooms, opens, wins, extra_foot=None):
    esp = unary_union(list(rooms.values()))
    foot = unary_union([esp.buffer(T, join_style="mitre")] + EXTRA + ([extra_foot] if extra_foot else []))
    return foot.difference(unary_union([esp] + list(opens.values()) + [w for w, _ in wins.values()]))

R = EX_ROOMS
# ---------------- PROPOSTA: ambientes ----------------
ROOMS = {
    # social (Casa Frontal + comodo de 414)
    "ESTAR - PE-DIREITO DUPLO": r(-18, 0, 690, 278),                       # sala + antiga sacada; fachada nova em x 672
    "TV / ESTAR": U(R["COMODO 414x275"], r(-33, 0, T, 275)),               # parede sala x 414 demolida
    "JANTAR / COZINHA": U(R["CORREDOR"], r(-18, 278, 390, T), r(-208, 393, 580, T),
                          R["COZINHA"], r(72, 408, T, 284), R["QUARTO 1"]),
    "LAVABO": R["BANHEIRO"],
    "ESCRITORIO / QUARTO 5": R["QUARTO 2"],
    # intima (Fundos 1)
    "HALL INTIMO": r(-592, 290, 204, 100),                                 # parede nova em x -607..-592
    "SUITE 1": U(R["COMODO B"], R["COMODO B2"]),
    "BANHO SUITE 1": U(R["COMODO A"], R["COMODO A2"]),
    "HOME THEATER": R["COMODO 430x275"],
    "HALL MASTER / ROUPARIA": R["COMODO E"],
    "SUITE MASTER": R["COMODO D"],
    "CLOSET MASTER": R["QUARTO SUITE"],
    "BANHO MASTER": R["BANHEIRO SUITE"],
    # servico e lazer (fundos)
    "LAVANDERIA / DESPENSA": R["COMODO 340x180"],
    "SERVICO EXTERNO": R["FAIXA EXTERNA 135"],
    "GOURMET": U(R["COMODO 340x390"], R["COMODO 340 (B)"]),
    "LAVABO PISCINA": R["BANHEIRO 150x150"],
    "HALL SUITE 3": R["CIRCULACAO 80"],
    "BANHO SUITE 3": R["COMODO 215x295"],                                   # unico ponto molhado novo
    "SUITE 3": R["COMODO 255x390"],
    "SUITE HOSPEDES": R["COMODO 400x400"],
    "BANHO HOSPEDES": R["BANHEIRO 240x80"],
}

# ---------------- PROPOSTA: vaos ----------------
manter = ["P70 BANHEIRO", "P70 QUARTO 2", "P70 414x430", "PASSAGEM 80", "PASSAGEM 77 D-E", "P60 BANHEIRO SUITE",
          "PASSAGEM 85", "P78 ENTRADA", "FAIXA ABERTA LADO", "FAIXA ABERTA FIM", "P70 215", "P70 255",
          "P60 BWC 150", "P60 BWC 240", "P80 CASA CIMA"]
OPENINGS = {k: EX_OPEN[k] for k in manter}
OPENINGS.update({
    "ACESSO HALL INTIMO": r(-388, 300, T, 85),
    "P80 SUITE 1": r(-607, 300, T, 80),
    "P70 BANHO SUITE 1": r(-549, 440, T, 70),
    "P80 HALL MASTER": r(-907, 100, T, 80),
    "P70 BANHO MASTER": r(-1172, 600, T, 70),
    "P80 GOURMET-SUITE 3": r(-1882, 0, T, 80),
    "PORTA CORRER GOURMET": r(-1695, 390, 160, T),
    "P80 LAVANDERIA": r(-1484.5, 180, 80, T),
})
manter_j = ["J 60x60/163", "J 150x120/95", "J 150x120/100 Q1", "J 150x120/100 Q2", "J 107x58/161",
            "J 56x37/195", "J 57x36/173", "J 147x107/100 A", "J 147x107/100 B", "J 60x40/150"]
WINDOWS = {k: EX_WIN[k] for k in manter_j}
WINDOWS.update({
    "FACHADA PANO DE VIDRO": (r(672, 0, T, 278), "v"),
    "J 150x120/100 SUITE 1": (r(-824.5, 692, 150, T), "h"),
    "J 150x120/100 MASTER": (r(-1107, 692, 150, T), "h"),
    "J 150x120/100 HOSPEDES": (r(-1967, 720, T, 150), "v"),
})
# portas (folha + arco): existentes mantidas + novas
EX_DOORS = {**F.DOORS, **B.DOORS, **C.DOORS, **D.DOORS}
DOORS = {k: EX_DOORS[k] for k in ["P70 BANHEIRO", "P70 QUARTO 2", "P70 414x430", "P60 BANHEIRO SUITE", "P78 ENTRADA",
                                    "P70 215", "P70 255", "P60 BWC 150", "P60 BWC 240", "P80 CASA CIMA"]}
DOORS.update({
    "P80 SUITE 1": ((-607, 300), (0, 1), (-1, 0), 80),
    "P70 BANHO SUITE 1": ((-534, 440), (0, 1), (1, 0), 70),
    "P80 HALL MASTER": ((-907, 100), (0, 1), (-1, 0), 80),
    "P70 BANHO MASTER": ((-1157, 600), (0, 1), (1, 0), 70),
    "P80 GOURMET-SUITE 3": ((-1882, 80), (0, -1), (-1, 0), 80),
    "P80 LAVANDERIA": ((-1484.5, 180), (1, 0), (0, -1), 80),
})

# ---------------- elementos novos (polilinhas fechadas) ----------------
PISCINA = r(-1800, 460, 250, 400)                     # 2,50 x 4,00 no patio entre o gourmet e a suite de hospedes
DECK = r(-1937, 420, 410, 467)
VAGAS = [r(E.X_GRADE_SAC + 10, 30, 470, 250), r(E.X_GRADE_SAC + 10, 330, 470, 250)]
CLARABOIAS = [r(-300, 90, 120, 100), r(-730, 90, 120, 100), r(-560, 310, 100, 60), r(-1090, 90, 120, 100)]
BANCADA = r(-180, 632, 420, 60)                       # bancada na parede da janela da cozinha (ponto existente)
ILHA = r(-60, 470, 220, 90)

NOTAS = [
    ("FACHADA NOVA: VOLUME COM PE-DIREITO DUPLO, PANO DE VIDRO E BRISE", (330, -70), 12),
    ("GARAGEM 2 VAGAS", (E.X_GRADE_SAC + 245, 300), 14),
    ("PORTAO NOVO", (E.X_RUA + 70, 350), 10),
    ("PASSARELA COBERTA / ACESSO AO LAZER (CORREDOR LATERAL)", (-500, 850), 14),
    ("PISCINA 2,50 x 4,00", (-1675, 660), 11),
    ("DECK", (-1880, 450), 9),
    ("CLARABOIA", (-240, 140), 7), ("CLARABOIA", (-670, 140), 7), ("CLARABOIA", (-1030, 140), 7),
    ("BANCADA", (30, 662), 8), ("ILHA", (50, 515), 8),
]
