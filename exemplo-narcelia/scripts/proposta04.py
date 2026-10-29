# Proposta 04 - revisao da 02 (marcacoes do arquiteto em 29/10): entrada social na fachada, recuo no lugar da sacada,
# jantar + cozinha ate o vidro, jardim reduzido ate a altura do lavabo, estar + TV, banhos reorganizados, gourmet sem banheiro.
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
EX_DOORS = {**F.DOORS, **B.DOORS, **C.DOORS, **D.DOORS}
EXTRA = [F.r(F.X_VIDRO, -T, F.SAC + T, T)]          # muro sobre a antiga sacada

def paredes(rooms, opens, wins):
    esp = unary_union(list(rooms.values()))
    foot = unary_union([esp.buffer(T, join_style="mitre")] + EXTRA)
    return foot.difference(unary_union([esp] + list(opens.values()) + [w for w, _ in wins.values()]))

R = EX_ROOMS
X_JD = -238                                                     # face do jardim reduzido (vidro alinhado c/ a face do lavabo, -223)
# ---------------- PROPOSTA: ambientes ----------------
ROOMS = {
    # social: estar + TV na fileira do corredor; jantar + cozinha ate o vidro (antiga sacada vira recuo)
    "ESTAR (PE-DIREITO DUPLO)": U(
        R["QUARTO 2"], r(372, 293, T, 399),                     # parede Q2 x corredor/Q1 demolida
        r(87, 293, 285, 100), r(87, 393, 285, T), R["QUARTO 1"]),
    "SALA DE TV": r(-208, 293, 295, 399),                      # antiga cozinha + trecho do corredor, junto ao lavabo
    "JANTAR / COZINHA": U(r(-18, 0, F.X_VIDRO + 18, 293),       # sala ate o vidro + parede sala x corredor/Q2
                          r(X_JD + T, 0, -18 - X_JD - T, 275)), # frente do comodo de 414 (ate a altura do lavabo)
    "LAVABO": R["BANHEIRO"],
    "JARDIM DE INVERNO": r(-447, 0, X_JD + 447, 275),           # reduzido; pode ser so poco de ventilacao
    # intima
    "CORREDOR 100": U(r(-373, 293, 165, 100), r(-388, 293, T, 100), R["CIRCULACAO"], r(-892, 290, 285, 100)),
    "SUITE 1": r(-892, 405, 343, 287),                          # comodo B sem o nicho (fica retangular)
    "BANHO SUITE 1": R["COMODO A"],
    "SUITE 2": R["COMODO 430x275"],
    "BANHO SUITE 2": r(-1157, 0, 250, 120),                     # parte de baixo do comodo E (antigo banho de servico)
    "BANHO MASTER": r(-1157, 135, 250, 140),                    # parte de cima do comodo E, entrada pelo closet
    "SUITE MASTER": R["COMODO D"],
    "CLOSET MASTER": R["QUARTO SUITE"],
    # servico e lazer
    "BANHO LAZER": R["BANHEIRO SUITE"],                         # antigo banho da master, porta p/ fora (gourmet/piscina)
    "AREA DE SERVICO COBERTA": R["COMODO 340x180"],
    "AREA DE SERVICO DESCOBERTA": R["FAIXA EXTERNA 135"],
    "GOURMET": r(C.X_J - 255, 0, C.X_H - C.X_J + 255, C.PROF),  # salao unico; banheiro da piscina incorporado
}

# ---------------- PROPOSTA: vaos ----------------
manter = ["P70 BANHEIRO", "FAIXA ABERTA LADO", "FAIXA ABERTA FIM", "P80 E"]   # servico fechado p/ o gourmet
OPENINGS = {k: EX_OPEN[k] for k in manter}
OPENINGS.update({
    "PORTA ENTRADA": r(672, 557, T, 120),                       # entrada social na fachada (lado da garagem)
    "P80 SUITE 1": r(-700, 390, 80, T),
    "P70 BANHO SUITE 1": r(-549, 600, T, 70),
    "P80 SUITE 2": EX_OPEN["PASSAGEM 80"],
    "P70 BANHO SUITE 2": r(-907, 20, T, 70),
    "P80 SUITE MASTER": r(-907, 300, T, 80),
    "PASSAGEM 90 CLOSET": r(-1172, 340, T, 90),                 # abertura master -> closet (banho pelo P80 existente)
    "P70 BANHO LAZER": r(-1377, 600, T, 70),
    "P80 SERVICO": r(-1484.5, 180, 80, T),
    "CORRER GOURMET 1": r(-1695, 390, 160, T),
    "CORRER GOURMET 2": r(-2089.5, 390, 200, T),
    "CORRER GOURMET 3": r(-2339.5, 390, 200, T),
    "CORRER GOURMET 4": r(-1860, 390, 140, T),
})
manter_j = ["J 60x60/163", "J 150x120/95", "J 150x120/100 Q1", "J 107x58/161", "J 56x37/195"]
WINDOWS = {k: EX_WIN[k] for k in manter_j}
WINDOWS.update({
    "PANO DE VIDRO JANTAR (RECUO)": (r(F.X_VIDRO, 0, T, 278), "v"),
    "ESQUADRIA FACHADA ESTAR": (r(672, 310, T, 230), "v"),
    "VIDRO JARDIM-COZINHA": (r(X_JD, 0, T, 275), "v"),
    "VIDRO JARDIM-CORREDOR": (r(-430, 275, 180, T), "h"),
    "J 150x120/100 SUITE 2 (P/ JARDIM)": (r(-462, 60, T, 150), "v"),
    "J 150x120/100 SUITE 1": (r(-824.5, 692, 150, T), "h"),
    "J 150x120/100 MASTER": (r(-1107, 692, 150, T), "h"),
})
DOORS = {k: EX_DOORS[k] for k in ["P70 BANHEIRO", "P80 E"]}
DOORS.update({
    "PORTA ENTRADA": ((672, 677), (0, -1), (-1, 0), 120),
    "P80 SUITE 1": ((-700, 405), (1, 0), (0, 1), 80),
    "P70 BANHO SUITE 1": ((-534, 600), (0, 1), (1, 0), 70),
    "P80 SUITE 2": ((-542, 275), (1, 0), (0, -1), 80),
    "P70 BANHO SUITE 2": ((-907, 20), (0, 1), (-1, 0), 70),
    "P80 SUITE MASTER": ((-907, 300), (0, 1), (-1, 0), 80),
    "P70 BANHO LAZER": ((-1362, 600), (0, 1), (1, 0), 70),
    "P80 SERVICO": ((-1484.5, 180), (1, 0), (0, -1), 80),
})
CORRER = ["CORRER GOURMET 1", "CORRER GOURMET 2", "CORRER GOURMET 3", "CORRER GOURMET 4"]

# ---------------- elementos novos ----------------
PISCINA = r(-2280, 620, 600, 300)                    # 6,00 x 3,00 no lugar da casa de cima (demolida)
DECK = r(-2367, 420, 670, 562)
VAGAS = [r(600, 727, 470, 250)]                      # garagem no corredor lateral
COBERTURA = r(687, -15, 314, F.Y_DIVISA + 15)        # cobertura com platibanda na frente (volumetria)
CLARABOIAS = []
BANCADA = r(-205, 0, 400, 60)                        # cozinha no fundo (bancada na divisa) + ilha; jantar junto ao vidro
ILHA = r(0, 185, 240, 80)
EXTRAS = [r(-2367, 100, 60, 220),                    # bancada / churrasqueira do gourmet
          r(340, 90, 180, 100)]                      # mesa de jantar
NOTAS = [
    ("COBERTURA COM PLATIBANDA - VOLUMETRIA DA FACHADA", (844, 150), 11),
    ("GARAGEM COBERTA (CORREDOR LATERAL)", (835, 870), 13),
    ("PORTAO GARAGEM", (E.X_RUA + 75, 850), 10),
    ("ENTRADA SOCIAL", (760, 617), 10),
    ("ESQUADRIA", (760, 425), 10),
    ("RECUO", (630, 170), 10), ("(ANTIGA SACADA)", (630, 140), 7),
    ("JARDIM FRONTAL", (1090, 300), 11),
    ("ABERTO P/ O CEU", (-342, 60), 8),
    ("PISCINA 6,00 x 3,00", (-1980, 770), 12),
    ("DECK", (-1600, 480), 10),
    ("CHURRASQUEIRA / BANCADA", (-2337, 340), 7),
    ("BANCADA", (-5, 30), 8), ("ILHA", (120, 225), 8), ("MESA", (430, 140), 8),
]
