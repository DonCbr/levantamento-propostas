import sys, math; sys.path.insert(0, sys.argv[1])
import frontal as F, gcad as G

G.clear()
G.ensure_layer("ARQ-GRADE", 6); G.ensure_layer("ARQ-EXTERNO", 9)

w = F.walls()
G.layer("ARQ-PAREDE")
for p in (list(w.geoms) if hasattr(w, "geoms") else [w]):
    G.pline(list(p.exterior.coords)[:-1])
    for h in p.interiors: G.pline(list(h.coords)[:-1])
G.app.ZoomExtents(); G.app.ZoomScaled(0.7, 1)

G.layer("ARQ-PORTA")
for nome, (h, c, o, wd) in F.DOORS.items():
    hx, hy = h
    G.line(h, (hx + o[0]*wd, hy + o[1]*wd))
    G.pline([(hx + wd*(c[0]*math.cos(a) + o[0]*math.sin(a)),
              hy + wd*(c[1]*math.cos(a) + o[1]*math.sin(a)))
             for a in [math.pi/2*i/16 for i in range(17)]], closed=False)

G.layer("ARQ-JANELA")
for nome, (geo, ori) in F.WINDOWS.items():
    x0, y0, x1, y1 = geo.bounds
    G.pline([(x0,y0),(x1,y0),(x1,y1),(x0,y1)])
    for f in (1/3, 2/3):
        if ori == "h": y = y0+(y1-y0)*f; G.line((x0,y),(x1,y))
        else:          x = x0+(x1-x0)*f; G.line((x,y0),(x,y1))

G.layer("ARQ-GRADE")
x0, y0, x1, y1 = F.GRADE.bounds
G.pline([(x0,y0),(x1,y0),(x1,y1),(x0,y1)])
for k in range(1, 12):
    y = y0 + (y1-y0)*k/12; G.line((x0-6,y),(x1+6,y))

G.layer("ARQ-EXTERNO")
x0, y0, x1, y1 = F.CAIXA.bounds
G.pline([(x0,y0),(x1,y0),(x1,y1),(x0,y1)]); G.line((x0,y0),(x1,y1)); G.line((x0,y1),(x1,y0))
G.line((-388-60, F.Y_DIVISA), (687+60, F.Y_DIVISA))   # divisa do corredor lateral

G.layer("ARQ-TEXTO")
for nome, geo in F.ROOMS.items():
    cx, cy = geo.centroid.coords[0]
    G.ctext(nome, cx, cy + 10, 16)
    G.ctext(f"{geo.area/1e4:.2f} m2", cx, cy - 14, 11)
cx, cy = F.SACADA.centroid.coords[0]; G.ctext("SACADA", cx, cy, 12)
G.ctext("GRADE C/ ACESSO", F.GRADE.bounds[2] + 60, 139, 9)
G.ctext("PORTA DE VIDRO", F.X_VIDRO + 7, -40, 10)
G.ctext("CAIXA DE LUZ", 613, F.Y_BOT + 60, 9)
G.ctext("CORREDOR LATERAL", 150, F.Y_BOT + 15 + 145, 16)
for nome, (geo, ori) in F.WINDOWS.items():
    if nome.startswith("J "):
        cx, cy = geo.centroid.coords[0]
        G.ctext(nome.split(" ")[1], cx + (40 if ori == "v" else 0), cy + (30 if ori == "h" else 0), 9)

G.layer("ARQ-COTA")
G.dim((250, F.Y_BOT + 15), (250, F.Y_DIVISA), (290, F.Y_BOT + 15))
G.app.ZoomExtents(); G.app.ZoomScaled(0.9, 1)
print("ok", G.ms.Count, "entidades")
