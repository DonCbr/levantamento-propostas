# Casa Frontal - geometria em cm, referencial da folha (x p/ direita, y p/ baixo).
# Origem = canto interno superior-esquerdo da sala (590 x 278).
# Na saida para o CAD: X = -x, Y = y  (giro de 180 graus).
from shapely.geometry import box
from shapely.ops import unary_union

T = 15  # espessura de parede
BON = 5  # boneca entre a porta e a parede perpendicular

def r(x0, y0, w, h):
    return box(x0, y0, x0 + w, y0 + h)

Y_CORR = 278 + T            # 293
Y_ROW = Y_CORR + 100 + T    # 408
PROF = 284                  # profundidade da fileira de comodos (igualada)
Y_BOT = Y_ROW + PROF        # 692 face interna da parede das janelas
DS = 18                     # recuo da sala p/ a grade ficar rente ao muro (face ext. do quarto 2)
PV = 80                     # folha de abrir da porta de vidro (ESTIMADA)
SAC = 100                   # largura da mini sacada (confirmada: 1 m)

ROOMS = {
    "SALA": r(-DS, 0, 590, 278),
    "CORREDOR": r(-373, Y_CORR, 373 + 372, 100),
    "BANHEIRO": r(-373, Y_ROW, 150, PROF),
    "COZINHA": r(-208, Y_ROW, 280, PROF),
    "QUARTO 1": r(87, Y_ROW, 285, PROF),
    "QUARTO 2": r(387, Y_CORR, 285, Y_BOT - Y_CORR),
}
X_VIDRO = 590 - DS          # face interna da parede de vidro
SACADA = r(X_VIDRO + T, 0, SAC, 278)

# Vaos de porta / passagem atravessando a parede
OPENINGS = {
    "PASSAGEM 87": r(-DS, 278, 87, T),
    "P70 BANHEIRO": r(-373 + BON, Y_ROW - T, 70, T),
    "P70 COZINHA": r(72 - BON - 70, Y_ROW - T, 70, T),
    "P70 QUARTO 1": r(87 + BON, Y_ROW - T, 70, T),
    "P70 QUARTO 2": r(372, Y_CORR + BON, T, 70),     # parede corredor x quarto 2
    "PORTA VIDRO": r(X_VIDRO, 278 - PV, T, PV),
}

def jan_h(xc, w):
    return r(xc - w / 2, Y_BOT, w, T)
# Janelas / esquadrias: (retangulo no vao, orientacao do eixo)
WINDOWS = {
    "J 60x60/163": (jan_h(-373 + 75, 60), "h"),
    "J 150x120/95": (jan_h(-208 + 140, 150), "h"),
    "J 150x120/100 Q1": (jan_h(87 + 142.5, 150), "h"),
    "J 150x120/100 Q2": (r(672, (Y_CORR + Y_BOT) / 2 - 75, T, 150), "v"),
    "PORTA DE VIDRO": (r(X_VIDRO, 0, T, 278 - PV), "v"),   # parte fixa
}

def walls():
    spaces = unary_union(list(ROOMS.values()))
    foot = unary_union([spaces.buffer(T, join_style="mitre"),
                        r(X_VIDRO, -T, SAC + T, T)])          # muro/parede sobre a sacada
    cut = unary_union([spaces] + list(OPENINGS.values())
                      + [w for w, _ in WINDOWS.values()])
    return foot.difference(cut)

# Portas: (dobradica, direcao fechada, direcao de abertura, largura)
DOORS = {
    "P70 BANHEIRO": ((-373 + BON, Y_ROW), (1, 0), (0, 1), 70),
    "P70 COZINHA": ((72 - BON, Y_ROW), (-1, 0), (0, 1), 70),
    "P70 QUARTO 1": ((87 + BON, Y_ROW), (1, 0), (0, 1), 70),
    "P70 QUARTO 2": ((387, Y_CORR + BON), (0, 1), (1, 0), 70),
    "PORTA VIDRO": ((X_VIDRO, 278), (0, -1), (-1, 0), PV),
}

# Grade da sacada (linha externa), com acesso
GRADE = r(X_VIDRO + T + SAC - 5, 0, 5, 278)   # face externa rente ao quarto 2 (687)
# Caixa de luz na face externa da parede das janelas, perto do canto
CAIXA = r(583, Y_BOT + T, 60, 20)
# Corredor lateral externo
CORR_LAT = 290
Y_DIVISA = Y_BOT + T + CORR_LAT
