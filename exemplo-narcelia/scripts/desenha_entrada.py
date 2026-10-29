import sys; sys.path.insert(0, sys.argv[1])
import entrada as E, frontal as F, gcad as G

G.layer("ARQ-EXTERNO")
G.line((F.GRADE.bounds[2], E.Y_TOPO), (E.X_RUA, E.Y_TOPO))              # divisa de cima
G.line((E.X_RUA, E.Y_TOPO), (E.X_RUA, E.Y_DIVISA))                    # limite c/ a rua
G.line((687 + 60, E.Y_DIVISA), (E.X_RUA, E.Y_DIVISA))                 # divisa do corredor

G.layer("ARQ-GRADE")
y0, y1 = E.Y_GRADE_BAIXO, E.Y_GRADE_BAIXO + 5
G.pline([(E.X_Q2_EXT, y0), (E.X_RUA, y0), (E.X_RUA, y1), (E.X_Q2_EXT, y1)])
n = 20
for k in range(1, n):
    x = E.X_Q2_EXT + (E.X_RUA - E.X_Q2_EXT) * k / n; G.line((x, y0 - 6), (x, y1 + 6))

G.layer("ARQ-TEXTO")
G.ctext("AREA DE ENTRADA", (E.X_GRADE_SAC + E.X_RUA) / 2, 360, 16)
G.ctext("GRADE", (E.X_Q2_EXT + E.X_RUA) / 2, E.Y_GRADE_BAIXO - 18, 9)
G.ctext("RUA", E.X_RUA + 120, 490, 22)
G.ctext("LIMITE DO TERRENO", E.X_RUA + 55, 140, 9)

G.layer("ARQ-COTA")
G.dim((E.X_GRADE_SAC, 40), (E.X_RUA, 40), (E.X_GRADE_SAC, 80))
G.dim((E.X_RUA, E.Y_TOPO), (E.X_RUA, E.Y_DIVISA), (E.X_RUA + 50, E.Y_TOPO))
G.dim((F.SACADA.bounds[0], 230), (F.GRADE.bounds[2], 230), (F.SACADA.bounds[0], 250))
G.app.ZoomExtents(); G.app.ZoomScaled(0.95, 1)
G.doc.Save()
print("entrada ok; frente do lote (cota):", E.Y_DIVISA - E.Y_TOPO, "cm")
