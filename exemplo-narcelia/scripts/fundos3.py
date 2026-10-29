# Folha 4, parte de cima: casa do fundo junto a divisa do corredor lateral.
# Mesmo referencial (x p/ a rua, y da divisa do fundo p/ o corredor).
from shapely.geometry import box
import fundos2 as C, frontal as F

T = 15
BON = 5

def r(x0, y0, w, h):
    return box(x0, y0, x0 + w, y0 + h)

Y_K1 = F.Y_DIVISA - T        # casa colada no muro da divisa do corredor lateral (982)
Y_K0 = Y_K1 - 400            # corredor entre o bloco principal e a casa fica com 162 (croqui 155)
X_K1 = C.X_FIM + T           # face do fundo (alinhada c/ o comodo de 255) -2367
X_K0 = X_K1 + 400            # face do lado da rua -1967
X_B0 = X_K0 + T              # banheiro 240x80 ao lado (lado da rua)

ROOMS = {
    "COMODO 400x400": r(X_K1, Y_K0, 400, 400),
    "BANHEIRO 240x80": r(X_B0, Y_K1 - 80, 240, 80),
}
MERGE = {}
OPENINGS = {
    "P60 BWC 240": r(X_K0, Y_K1 - BON - 60, T, 60),
    "P80 CASA CIMA": r(X_K0, Y_K0 + 20, T, 80),          # de frente p/ a area de 330 (boneca ESTIMADA 20)
}
WINDOWS = {
    "J 60x40/150": (r(X_B0 + 240, Y_K1 - 40 - 30, T, 60), "v"),
}
DOORS = {
    "P60 BWC 240": ((X_K0, Y_K1 - BON - 60), (0, 1), (-1, 0), 60),
    "P80 CASA CIMA": ((X_K0, Y_K0 + 20), (0, 1), (-1, 0), 80),
}
LOUCAS = [
    list(r(X_B0 + 60, Y_K1 - 80 - T - 65, 65, 65).exterior.coords)[:-1],   # tanque da area de 330 (ESTIMADO)
    list(r(X_K1, C.PROF + T + 5, 65, 90).exterior.coords)[:-1],            # tanque no corredor de 155 (ESTIMADO)
]
NOTES = [
    ("AREA ABERTA (330)", (X_B0 + 120, Y_K0 + 120), 9),
    ("TANQUE", (X_B0 + 92, Y_K1 - 80 - T - 75), 7),
    ("CORREDOR 162 (CROQUI 155)", (X_K1 + 250, C.PROF + T + 81), 11),
    ("TANQUE", (X_K1 + 32, C.PROF + T + 105), 7),
]
