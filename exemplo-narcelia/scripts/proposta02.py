# Proposta 02 - estudo preliminar (casa unica para venda), a partir das marcacoes do arquiteto.
# Criterio: menor intervencao que atenda o programa. Existente = levantamento.
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
# ---------------- PROPOSTA: ambientes ----------------
ROOMS = {
    # social: conceito aberto na Casa Frontal
    "ESTAR / JANTAR (PE-DIREITO DUPLO NO ESTAR)": U(
        R["QUARTO 2"], r(372, 293, T, 399),                     # parede Q2 x corredor/Q1 demolida
        r(-208, 293, 580, 100), r(-208, 393, 580, T),           # trecho do corredor + parede corredor x Q1/cozinha
        R["COZINHA"], r(72, 408, T, 284), R["QUARTO 1"]),
    "COZINHA COM ILHA": r(-18, 0, 690, 293),                    # sala + antiga sacada + parede sala x corredor/Q2
    "LAVABO": R["BANHEIRO"],
    "JARDIM DE INVERNO": R["COMODO 414x275"],                   # aberto p/ o ceu, fechamentos em vidro
    # intima
    "CORREDOR 100": U(r(-373, 293, 165, 100), r(-388, 293, T, 100), R["CIRCULACAO"], r(-892, 290, 285, 100)),
    "SUITE 1": r(-892, 405, 343, 287),                          # comodo B sem o nicho (fica retangular)
    "BANHO SUITE 1": R["COMODO A"],
    "SUITE 2": R["COMODO 430x275"],
    "BANHO SUITE 2": r(-1157, 135, 250, 140),                  # parte de cima do comodo E
    "BANHO SERVICO": r(-1157, 0, 250, 120),                     # parte de baixo do comodo E
    "SUITE MASTER": R["COMODO D"],
    "BANHO MASTER": R["BANHEIRO SUITE"],
    "CLOSET MASTER": R["QUARTO SUITE"],
    # servico e lazer
    "AREA DE SERVICO COBERTA": R["COMODO 340x180"],
    "AREA DE SERVICO DESCOBERTA": R["FAIXA EXTERNA 135"],
    "GOURMET": U(R["COMODO 340x390"], R["COMODO 340 (B)"], R["CIRCULACAO 80"], R["COMODO 215x295"], R["COMODO 255x390"],
                 r(-1882, 0, T, 225), r(-2097, 80, 215, T), r(-2112, 0, T, 390)),   # paredes internas demolidas
    "BANHEIRO PISCINA": R["BANHEIRO 150x150"],
}

# ---------------- PROPOSTA: vaos ----------------
manter = ["P70 BANHEIRO", "P60 BANHEIRO SUITE", "PASSAGEM 85", "P78 ENTRADA", "FAIXA ABERTA LADO",
          "FAIXA ABERTA FIM", "P60 BWC 150"]
OPENINGS = {k: EX_OPEN[k] for k in manter}
OPENINGS.update({
    "PORTA ENTRADA": r(420, F.Y_BOT, 120, T),                   # entrada lateral, pela garagem (corredor lateral)
    "P80 SUITE 1": r(-700, 390, 80, T),
    "P70 BANHO SUITE 1": r(-549, 600, T, 70),
    "P80 SUITE 2": EX_OPEN["PASSAGEM 80"],
    "P70 BANHO SUITE 2": r(-907, 180, T, 70),
    "P70 BANHO SERVICO": r(-1172, 20, T, 70),
    "P80 SUITE MASTER": r(-907, 300, T, 80),
    "P70 BANHO MASTER": r(-1172, 600, T, 70),
    "P80 SERVICO": r(-1484.5, 180, 80, T),
    "CORRER GOURMET 1": r(-1695, 390, 160, T),
    "CORRER GOURMET 2": r(-2089.5, 390, 200, T),
    "CORRER GOURMET 3": r(-2339.5, 390, 200, T),
})
manter_j = ["J 60x60/163", "J 150x120/95", "J 150x120/100 Q1", "J 107x58/161", "J 56x37/195", "J 57x36/173"]
WINDOWS = {k: EX_WIN[k] for k in manter_j}
WINDOWS.update({
    "FACHADA PANO DE VIDRO": (r(672, 0, T, 278), "v"),
    "ESQUADRIA FACHADA ESTAR": (r(672, 330, T, 320), "v"),     # frente livre p/ esquadrias
    "VIDRO JARDIM-COZINHA": (r(-33, 0, T, 275), "v"),
    "VIDRO JARDIM-CORREDOR": (r(-360, 275, 300, T), "h"),
    "J 150x120/100 SUITE 2 (P/ JARDIM)": (r(-462, 60, T, 150), "v"),
    "J 150x120/100 SUITE 1": (r(-824.5, 692, 150, T), "h"),
    "J 150x120/100 MASTER": (r(-1107, 692, 150, T), "h"),
})
DOORS = {k: EX_DOORS[k] for k in ["P70 BANHEIRO", "P60 BANHEIRO SUITE", "P78 ENTRADA", "P60 BWC 150"]}
DOORS.update({
    "PORTA ENTRADA": ((420, F.Y_BOT + T), (1, 0), (0, -1), 120),
    "P80 SUITE 1": ((-700, 405), (1, 0), (0, 1), 80),
    "P70 BANHO SUITE 1": ((-534, 600), (0, 1), (1, 0), 70),
    "P80 SUITE 2": ((-542, 275), (1, 0), (0, -1), 80),
    "P70 BANHO SUITE 2": ((-907, 180), (0, 1), (-1, 0), 70),
    "P70 BANHO SERVICO": ((-1157, 20), (0, 1), (1, 0), 70),
    "P80 SUITE MASTER": ((-907, 300), (0, 1), (-1, 0), 80),
    "P70 BANHO MASTER": ((-1157, 600), (0, 1), (1, 0), 70),
    "P80 SERVICO": ((-1484.5, 180), (1, 0), (0, -1), 80),
})
CORRER = ["CORRER GOURMET 1", "CORRER GOURMET 2", "CORRER GOURMET 3"]

# ---------------- elementos novos ----------------
PISCINA = r(-2280, 620, 600, 300)                    # 6,00 x 3,00 no lugar da casa de cima (demolida)
DECK = r(-2367, 420, 670, 562)
VAGAS = [r(600, 727, 470, 250)]                      # garagem no corredor lateral (recuada p/ liberar a entrada)
COBERTURA = r(687, -15, 314, F.Y_DIVISA + 15)        # cobertura com platibanda na frente (volumetria)
CLARABOIAS = []
BANCADA = r(80, 0, 400, 60)                          # cozinha: bancada na parede da divisa + ilha
ILHA = r(250, 90, 240, 90)
EXTRAS = [r(-2367, 100, 60, 220)]                    # bancada / churrasqueira do gourmet
NOTAS = [
    ("COBERTURA COM PLATIBANDA - VOLUMETRIA DA FACHADA", (844, 150), 11),
    ("GARAGEM COBERTA (CORREDOR LATERAL)", (835, 870), 13),
    ("PORTAO GARAGEM", (E.X_RUA + 75, 850), 10),
    ("ENTRADA SOCIAL (PELA GARAGEM)", (480, 760), 10),
    ("ESQUADRIAS NA FACHADA", (760, 490), 10),
    ("JARDIM FRONTAL", (1090, 300), 11),
    ("ABERTO P/ O CEU - FECHAMENTO EM VIDRO", (-240, 60), 8),
    ("PISCINA 6,00 x 3,00", (-1980, 770), 12),
    ("DECK", (-1600, 480), 10),
    ("CHURRASQUEIRA / BANCADA", (-2337, 340), 7),
    ("BANCADA", (280, 30), 8), ("ILHA", (370, 135), 8),
]
