# Folha 4 (outra casa do fundo) - mesmo referencial (x p/ a rua, y da divisa do fundo p/ o corredor).
# Folha no mesmo sentido da Fundos 1. Comeca pelo comodo de 180 que encaixa no fundo da suite.
from shapely.geometry import box, Point

T = 15
BON = 5

def r(x0, y0, w, h):
    return box(x0, y0, x0 + w, y0 + h)

X_E_EXT = -1172              # face externa da parede do comodo E (alinhada c/ a suite)
X_SUITE_EXT = -1362 - T      # face externa da parede de tras da suite (-1377)
L_FX = 135                   # faixa externa atras da suite
X_CASA = X_SUITE_EXT - L_FX  # face da parede da casa nova (cotas 205/85) = -1512
Y_180 = 180
Y_FX0 = Y_180 + T            # inicio da faixa (= inicio do quarto da suite) 195
Y_ENT = Y_FX0 + 100          # fim da entrada coberta (137x100)
Y_FX1 = Y_FX0 + 400          # fim da faixa (cota 400)
# Bloco principal (390 de profundidade a partir da divisa)
PROF = 390
X_H = X_CASA - T            # face do comodo de 340 do lado da entrada (-1527)
X_HI = X_H - 340            # face do comodo de 340 do lado do 215 (-1867)
X_I = X_HI - T              # face do comodo de 215 do lado do 340 (-1882)
X_IJ = X_I - 215            # (-2097)
X_J = X_IJ - T              # (-2112)
X_FIM = X_J - 255 - T       # face externa do fundo do bloco (-2382)
Y_CIR = 80                  # circulacao junto a divisa, embaixo do comodo de 215
Y_BH = PROF - 150           # face do banheiro 150x150 (240)

ROOMS = {
    "COMODO 340x180": r(X_CASA, 0, X_E_EXT - X_CASA, Y_180),   # 190 + 15 + 135
    "FAIXA EXTERNA 135": r(X_CASA, Y_FX0, L_FX, Y_FX1 - Y_FX0),
    "COMODO 340x390": r(X_HI, 0, 340, Y_BH - T),
    "COMODO 340 (B)": r(X_HI + 150 + T, Y_BH - T, 340 - 150 - T, PROF - Y_BH + T),   # trecho ao lado do banheiro (croqui 233)
    "BANHEIRO 150x150": r(X_HI, Y_BH, 150, 150),
    "CIRCULACAO 80": r(X_IJ, 0, 215, Y_CIR),
    "COMODO 215x295": r(X_IJ, Y_CIR + T, 215, PROF - Y_CIR - T),
    "COMODO 255x390": r(X_J - 255, 0, 255, PROF),
}
MERGE = {"COMODO 340 (B)": "COMODO 340x390"}
OPENINGS = {
    "PASSAGEM 85": r(X_CASA - T, 0, T, 85),                       # p/ o proximo comodo (A CONFERIR)
    "P78 ENTRADA": r(X_CASA - T, Y_ENT - BON - 78, T, 78),
    "FAIXA ABERTA LADO": r(X_CASA - T - 1, PROF + T, T + 1, Y_FX1 - PROF),   # depois do bloco de 390
    "FAIXA ABERTA FIM": r(X_CASA - T - 1, Y_FX1 - 1, L_FX + T + 1, T + 2),
    "ABERTO 340-CIRC": r(X_I, 0, T, Y_CIR),
    "P70 215": r(X_I - BON - 70, Y_CIR, 70, T),
    "P70 255": r(X_J, BON, T, 70),
    "P60 BWC 150": r(X_HI + BON, Y_BH - T, 60, T),
}
WINDOWS = {
    "J 97x108/104": (r(X_CASA + L_FX / 2 - 48.5, Y_180, 97, T), "h"),
    "J 57x36/173": (r(X_HI + 75 - 28.5, PROF, 57, T), "h"),
    "J 147x107/100 A": (r(X_IJ + 107.5 - 73.5, PROF, 147, T), "h"),
    "J 147x107/100 B": (r(X_J - 127.5 - 73.5, PROF, 147, T), "h"),
}
DOORS = {
    "P78 ENTRADA": ((X_CASA - T, Y_ENT - BON), (0, -1), (-1, 0), 78),
    "P70 215": ((X_I - BON, Y_CIR + T), (-1, 0), (0, 1), 70),
    "P70 255": ((X_J, BON), (0, 1), (-1, 0), 70),
    "P60 BWC 150": ((X_HI + BON, Y_BH), (1, 0), (0, 1), 60),
}
# Loucas / equipamentos: polilinhas fechadas (referencial da folha)
def circ(cx, cy, rr, n=20):
    return list(Point(cx, cy).buffer(rr, n // 4).exterior.coords)[:-1]
TQ = r(X_SUITE_EXT - 60, Y_FX0 + 180, 60, 120)   # tanque duplo (POSICAO ESTIMADA)
LOUCAS = [list(TQ.exterior.coords)[:-1],
          circ(X_SUITE_EXT - 30, Y_FX0 + 210, 22), circ(X_SUITE_EXT - 30, Y_FX0 + 270, 22)]
NOTES = [
    ("ENTRADA COBERTA", (X_CASA + L_FX / 2, Y_FX0 + 55), 9),
    ("TANQUE DUPLO", (X_SUITE_EXT - 30, Y_FX0 + 165), 7),
    ("CROQUI 200 + 135", (X_E_EXT - 170, 40), 7),
]
