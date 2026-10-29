# Folha ENTRADA - mesmo referencial da Casa Frontal (x p/ a rua, y p/ baixo).
import frontal as F

X_GRADE_SAC = F.GRADE.bounds[2]          # face externa da grade da sacada (710)
X_Q2_EXT = 672 + F.T                     # face externa do quarto 2 (687)
LARG_ENTRADA = 485
X_RUA = X_GRADE_SAC + LARG_ENTRADA       # limite frontal do terreno (1195)
Y_TOPO = -F.T                            # divisa de cima (face externa da sala)
Y_GRADE_BAIXO = F.Y_BOT + F.T            # alinhada a parede das janelas (707)
Y_DIVISA = F.Y_DIVISA                    # divisa do corredor lateral (997)
