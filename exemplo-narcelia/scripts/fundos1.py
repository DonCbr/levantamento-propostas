# Fundos 1 - mesmo referencial da Casa Frontal (x p/ a rua, y da divisa do fundo p/ o corredor).
# A folha do croqui esta girada 180 graus em relacao a da Casa Frontal.
# Paredes de 15 cm, cotas internas. Itens marcados (A CONFERIR) sao estimados.
from shapely.geometry import box
from shapely.ops import unary_union

T = 15
BON = 5   # boneca entre a porta e a parede perpendicular
BON_B = 90  # boneca da porta de entrada do comodo B
BON_D = 114 # boneca da porta de entrada do comodo D
Y_CIRC = 290 + 100           # face da parede circulacao x comodo A (circulacao 100)

def r(x0, y0, w, h):
    return box(x0, y0, x0 + w, y0 + h)

X_BWC = -388                 # face externa da parede do banheiro da Casa Frontal (parede comum)
X_BD = -892                  # face da parede entre os comodos B e D (linha do 395)
Y_CORR = 692                 # alinhada com a Casa Frontal (croqui somava 676: 268 + 15 + 393)
Y_JOG = 552                  # degrau entre comodo A e B (A CONFERIR - estimado do croqui)
X_AB_SUP = -607              # face do comodo B na parte de cima (285 de largura)
X_COL = X_BD - T - 250 - T  # face interna da suite do fundo (alinhada c/ a parede do comodo D)
Y_DE = 275                  # face do comodo E: parede D x E na linha da bancada/circulacao (medido E 268 / D 395)
L_COL = 190                 # largura da suite do fundo
Y_Q0 = 180 + T              # quarto da suite comeca apos o comodo de 180 da outra casa (= inicio da porta do E)
Y_BWC = Y_CORR - 139        # face do banheiro da suite (banheiro 139; quarto fica com 343)
Y_DEG = Y_BWC - T - 95      # degrau de 11 (ESTIMADO do croqui: ~95 da parede do banheiro)

ROOMS = {
    "COMODO 414x275": r(-447, 0, 414, 275),            # croqui diz 485 (A CONFERIR)
    "COMODO 430x275": r(X_BD, 0, 430, 275),             # croqui 270; parede da bancada alinhada c/ a circulacao
    "COMODO A": r(X_BWC - 146, Y_CIRC + T, 146, Y_CORR - Y_CIRC - T),
    "COMODO A2": r(X_AB_SUP + T, Y_JOG + T, (X_BWC - 146) - (X_AB_SUP + T), Y_CORR - Y_JOG - T),
    "CIRCULACAO": r(X_AB_SUP, 290, X_BWC - X_AB_SUP, Y_CIRC - 290),
    "COMODO B": r(X_BD, 290, 285, Y_CORR - 290),
    "COMODO B2": r(X_AB_SUP, Y_CIRC + T, 343 - 285, Y_JOG - Y_CIRC - T),
    "COMODO D": r(X_BD - T - 250, Y_DE + T, 250, Y_CORR - Y_DE - T),   # croqui 393/395
    "COMODO E": r(X_BD - T - 250, 0, 250, Y_DE),   # alinhado c/ o D (croqui 238 x 268)
    "QUARTO SUITE": r(X_COL - L_COL, Y_Q0, L_COL, Y_BWC - T - Y_Q0),   # fundo (junto a divisa) e da outra casa
    "BANHEIRO SUITE": r(X_COL - L_COL, Y_BWC, L_COL, Y_CORR - Y_BWC),
}
# Salas formadas por mais de um retangulo (rotulo so no principal)
MERGE = {"COMODO A2": "COMODO A", "COMODO B2": "COMODO B"}

OPENINGS = {
    "P70 414x430": r(-462, 275 - BON - 70, T, 70),
    "PASSAGEM 80": r(-542, 275, 80, T),
    "P70 A": r(-497, Y_CIRC, 70, T),
    "P80 ENTRADA B": r(X_AB_SUP - BON_B - 80, Y_CORR, 80, T),
    "P82 ENTRADA D": r(X_BD - T - BON_D - 82, Y_CORR, 82, T),
    "P80 E": r(X_COL, Y_Q0, T, 80),   # parede E x suite
    "P60 BANHEIRO SUITE": r(X_COL - L_COL + BON, Y_BWC - T, 60, T),
    "PASSAGEM 77 D-E": r(X_BD - T - 77, Y_DE, 77, T),
}

WINDOWS = {
    "J 107x58/161": (r(-535, Y_CORR, 107, T), "h"),
    "J 56x37/195": (r(X_COL - L_COL / 2 - 28, Y_CORR, 56, T), "h"),
    "BANCADA 200x100": (r(-825, 275, 200, T), "h"),   # passa-prato entre B e o comodo de 430
}

DOORS = {
    "P70 414x430": ((-447, 275 - BON), (0, -1), (1, 0), 70),   # abre p/ o comodo de 414
    "P70 A": ((-497, Y_CIRC + T), (1, 0), (0, 1), 70),
    "P80 ENTRADA B": ((X_AB_SUP - BON_B, Y_CORR), (-1, 0), (0, -1), 80),
    "P82 ENTRADA D": ((X_BD - T - BON_D, Y_CORR), (-1, 0), (0, -1), 82),
    "P80 E": ((X_COL + T, Y_Q0 + 80), (0, -1), (1, 0), 80),
    "P60 BANHEIRO SUITE": ((X_COL - L_COL + BON, Y_BWC - T), (1, 0), (0, -1), 60),
}

NOTES = [
    ("DEGRAU 10", (X_AB_SUP - BON_B - 40, Y_CORR + 45), 9),
    ("DEGRAU 8", (X_BD - T - 38, 240), 8),
    ("414 (CROQUI 485) A CONFERIR", (-240, 60), 9),
    ("DEGRAU 11 (POSICAO A CONFERIR)", (X_COL - L_COL / 2, Y_DEG + 12), 7),
]
