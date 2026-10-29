# Layout (mobiliario, loucas, paisagismo) da Proposta 04 - cm, referencial da folha (x p/ a rua, y da divisa do fundo p/ o corredor).
# Usado pela planta de layout no GstarCAD (desenha_layout04.py) e pela planta humanizada (humanizada04.py).
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shapely.geometry import box, Point, LineString
from shapely import affinity
import proposta04 as P, fundos2 as C

R = lambda x0, y0, w, h: box(x0, y0, x0 + w, y0 + h)
CI = lambda cx, cy, r: Point(cx, cy).buffer(r, 12)
EL = lambda cx, cy, rx, ry: affinity.scale(Point(cx, cy).buffer(1, 12), rx, ry)
L = lambda *pts: LineString(pts)

def RR(x0, y0, w, h, rad):
    rad = max(0.5, min(rad, w / 2 - 0.5, h / 2 - 0.5))
    return box(x0 + rad, y0 + rad, x0 + w - rad, y0 + h - rad).buffer(rad, 4)

def poe(pecas, x0, y0, ang=0):
    # gira a peca (costas em y=0) e encosta o canto minimo do contorno em (x0, y0).
    # ang: 0 = costas p/ y menor | 180 = costas p/ y maior | 90 = costas p/ x maior | 270 = costas p/ x menor
    g = [(affinity.rotate(p, ang, origin=(0, 0)), s) for p, s in pecas]
    mx = min(p.bounds[0] for p, _ in g); my = min(p.bounds[1] for p, _ in g)
    return [(affinity.translate(p, x0 - mx, y0 - my), s) for p, s in g]

# ---------------- pecas (locais: largura w em x, costas em y = 0) ----------------
def cama(w=160, l=200):
    return [(RR(0, 0, w, l, 4), "cama"), (R(0, 0, w, 8), "madeira"),
            (RR(8, 14, w / 2 - 12, 34, 8), "travesseiro"), (RR(w / 2 + 4, 14, w / 2 - 12, 34, 8), "travesseiro"),
            (RR(0, l * 0.38, w, l * 0.62, 4), "lencol"), (L((0, l * 0.38 + 16), (w, l * 0.38 + 16)), "linha"),
            (R(0, l * 0.76, w, l * 0.13), "manta")]

def criado(w=40, d=40):
    return [(RR(0, 0, w, d, 2), "madeira"), (CI(w / 2, d / 2 + 2, 9), "luminaria")]

def armario(w, d=60):
    n = max(1, round(w / 55))
    return [(R(0, 0, w, d), "armario"), (L((0, d / 2), (w, d / 2)), "linha")] + \
           [(L((i * w / n, 0), (i * w / n, d)), "linha") for i in range(1, n)]

def sofa(w, d=90):
    n = max(1, round((w - 40) / 75)); cw = (w - 40) / n
    return [(RR(0, 0, w, d, 6), "estofado2")] + \
           [(RR(20 + i * cw + 2, 22, cw - 4, d - 24, 5), "almofada") for i in range(n)]

def rack(w, d=45):
    return [(R(0, 0, w, d), "madeira"), (RR(w * 0.12, 2, w * 0.76, 6, 1), "tv")]

def bancada_coz(w, d=60, cook=None, cuba=None):
    p = [(R(0, 0, w, d), "bancada")]
    if cook is not None:
        p += [(R(cook, 8, 60, 46), "inox_escuro")] + \
             [(CI(cook + a, b, 7), "queimador") for a in (15, 45) for b in (20, 42)]
    if cuba is not None:
        p += [(RR(cuba, 10, 55, 38, 4), "inox"), (CI(cuba + 27.5, 29, 3), "ralo")]
    return p

def geladeira(w=75, d=70):
    return [(R(0, 0, w, d), "inox"), (L((0, d - 4), (w, d - 4)), "linha")]

def torre(w=60, d=60):
    return [(R(0, 0, w, d), "armario"), (R(8, d - 22, w - 16, 16), "inox_escuro")]

def vaso():
    return [(RR(0, 0, 40, 18, 3), "loucas"), (EL(20, 42, 17, 23), "loucas"), (EL(20, 44, 10, 15), "loucas2")]

def cuba_banho(w, d=50):
    return [(R(0, 0, w, d), "bancada"), (EL(w / 2, d * 0.55, min(20, w / 2 - 6), 14), "loucas"), (CI(w / 2, d * 0.55, 2), "ralo")]

def maquina(w=60, d=65):
    return [(R(0, 0, w, d), "loucas"), (CI(w / 2, d / 2 + 3, 20), "vidro")]

def carro():
    return [(RR(0, 0, 180, 440, 45), "carro"), (RR(14, 120, 152, 70, 12), "vidro_carro"),
            (RR(18, 190, 144, 170, 15), "carro2"), (RR(20, 360, 140, 45, 12), "vidro_carro")]

def espreguicadeira():
    return [(RR(0, 0, 65, 190, 8), "madeira"), (RR(5, 5, 55, 180, 6), "almofada_clara"), (RR(8, 8, 49, 40, 6), "travesseiro")]

def mesa(x0, y0, w, d, n, cab=False):
    p = []
    for i in range(n):
        cx = x0 + w * (i + 0.5) / n
        p += [(RR(cx - 22, y0 - 38, 44, 44, 5), "cadeira"), (RR(cx - 22, y0 + d - 6, 44, 44, 5), "cadeira")]
    if cab:
        cy = y0 + d / 2
        p += [(RR(x0 - 38, cy - 22, 44, 44, 5), "cadeira"), (RR(x0 + w - 6, cy - 22, 44, 44, 5), "cadeira")]
    return p + [(RR(x0, y0, w, d, 4), "mesa")]

def box_(x0, y0, w, h, *vidros):
    return [(R(x0, y0, w, h), "box"), (CI(x0 + w / 2, y0 + h / 2, 4), "ralo")] + [(L(*v), "vidro_linha") for v in vidros]

arvore = lambda cx, cy, r: [(CI(cx, cy, r), "arvore")]
arbusto = lambda cx, cy, r=22: [(CI(cx, cy, r), "arbusto")]
vaso_planta = lambda cx, cy, r=28: [(CI(cx, cy, r), "vaso_planta")]

# ---------------- pisos externos (desenhados antes dos ambientes) ----------------
LOTE = R(C.X_FIM, -15, 1172 - C.X_FIM, 997 + 15)
EXTERNOS = [
    (LOTE, "grama"),
    (R(-1377, 707, 1172 + 1377, 275), "intertravado"),          # corredor lateral + garagem
    (R(687, 0, 314, 707), "porcelanato_ext"),                    # acesso coberto (sob a platibanda)
    (R(1001, 562, 156, 120), "pedra"),                           # caminho do portao ate a porta
    (R(587, 0, 100, 278), "deck"),                               # recuo (antiga sacada)
    (R(-2367, 405, 670, 577), "deck"),
    (P.PISCINA, "borda"), (P.PISCINA.buffer(-20, join_style="mitre"), "agua"),
    (R(-1377, 952, 1960, 30), "canteiro"),                       # canteiro junto ao muro do corredor
]
MUROS = [R(C.X_FIM, 982, 1172 - C.X_FIM, 15), R(C.X_FIM, 405, 15, 577), R(687, -15, 470, 15)]
GRADIL = [R(1157, -15, 15, 1012)]

# ---------------- mobiliario ----------------
# m(ambiente, item, dimensao, pecas): desenha e registra no quadro de mobiliario (tab=False: so desenha, ex. tapetes).
# t3d = tipo do modelo no 3D web (catalogo em apresentacao-3d/modelo.html); ang = giro usado em poe(); extras -> parametros do modelo.
# mp(...) = m(...) com poe() embutido, para o giro do 3D sair igual ao da planta.
PECAS, MOB, ITENS3D = [], [], []
def m(amb, item, dim, pecas, tab=True, t3d=None, ang=0, **p3d):
    PECAS.extend(pecas)
    if tab: MOB.append((amb, item, dim))
    if t3d:
        x0 = min(g.bounds[0] for g, _ in pecas); y0 = min(g.bounds[1] for g, _ in pecas)
        x1 = max(g.bounds[2] for g, _ in pecas); y1 = max(g.bounds[3] for g, _ in pecas)
        w, d = ((y1 - y0), (x1 - x0)) if ang % 180 == 90 else ((x1 - x0), (y1 - y0))
        ITENS3D.append(dict(t=t3d, c=[round((x0 + x1) / 2, 1), round((y0 + y1) / 2, 1)], w=round(w, 1), d=round(d, 1), ang=ang, **p3d))
def mp(amb, item, dim, pecas, x0, y0, ang=0, **kw): m(amb, item, dim, poe(pecas, x0, y0, ang), ang=ang, **kw)
def cadeiras(amb, mz, t3d="cadeira_jantar"):
    # cadeiras de mesa(): o giro faz cada uma olhar p/ o centro da mesa
    (mx0, my0, mx1, my1) = mz[-1][0].bounds
    for g, st in mz[:-1]:
        cx, cy = g.centroid.coords[0]
        ang = 0 if cy < my0 else 180 if cy > my1 else 270 if cx < mx0 else 90
        m(amb, "Cadeira", "44 × 44", [(g, st)], t3d=t3d, ang=ang)
add = PECAS.extend
A = "SALA DE ESTAR"
m(A, "Tapete", "280 × 270", [(R(230, 390, 280, 270), "tapete")], tab=False, t3d="tapete")
mp(A, "Sofá 3 lugares", "240 × 95", sofa(240, 95), 250, 597, 180, t3d="sofa")
mp(A, "Poltrona", "78 × 82", sofa(78, 82), 270, 395, 0, t3d="poltrona"); mp(A, "Poltrona", "78 × 82", sofa(78, 82), 392, 395, 0, t3d="poltrona")
m(A, "Mesa de centro", "100 × 50", [(RR(320, 510, 100, 50, 6), "madeira")], t3d="mesa_centro")
m(A, "Vaso com planta", "Ø 50", vaso_planta(640, 330), t3d="planta_grande"); m(A, "Vaso com planta", "Ø 50", vaso_planta(120, 655, 24), t3d="planta_grande")
A = "SALA DE TV"
m(A, "Tapete", "230 × 240", [(R(-150, 410, 230, 240), "tapete")], tab=False, t3d="tapete")
mp(A, "Rack + TV", "180 × 45", rack(180), -208, 440, 270, t3d="rack_tv")
mp(A, "Sofá 3 lugares", "220 × 95", sofa(220, 95), -10, 420, 90, t3d="sofa")
m(A, "Mesa de centro", "70 × 60", [(RR(-115, 495, 60, 70, 6), "madeira")], t3d="mesa_centro_redonda")
A = "JANTAR / COZINHA"
mp(A, "Bancada c/ cooktop e cuba (travertino)", "400 × 60", bancada_coz(400, 60, cook=230, cuba=60), -205, 0, 0, t3d="bancada_cozinha", cook=230, cuba=60)
mp(A, "Refrigerador inox", "75 × 70", geladeira(), -223, 205, 180, t3d="geladeira")
mp(A, "Torre quente (fornos)", "60 × 60", torre(), -148, 215, 180, t3d="torre")
m(A, "Ilha (travertino)", "240 × 80", [(P.ILHA, "bancada")], t3d="ilha")
for x in (45, 100, 155, 210): m(A, "Banqueta", "Ø 34", [(CI(x, 285, 17), "cadeira")], t3d="banqueta", ang=180)
mz = mesa(340, 90, 180, 100, 3)
m(A, "Mesa de jantar (6 lugares)", "180 × 100", mz[-1:], t3d="mesa_jantar"); cadeiras(A, mz)
m("RECUO", "Vaso com planta", "Ø 56", vaso_planta(637, 50), t3d="planta_pequena"); m("RECUO", "Vaso com planta", "Ø 56", vaso_planta(637, 228), t3d="planta_pequena")
A = "LAVABO"
mp(A, "Bancada c/ cuba", "90 × 50", cuba_banho(90), -273, 500, 90, tab=False, t3d="bancada_banho")
mp(A, "Bacia", "40 × 65", vaso(), -330, 627, 180, tab=False, t3d="bacia")
A = "JARDIM DE INVERNO"
m(A, "Árvore", "Ø 140", arvore(-342, 140, 70), tab=False, t3d="arvore")
for x in (-425, -260):
    for y in (28, 248): m(A, "Arbusto", "Ø 40", arbusto(x, y, 20), tab=False, t3d="arbusto")
A = "SUÍTE 01"
m(A, "Tapete", "160 × 215", [(R(-780, 460, 160, 215), "tapete")], tab=False, t3d="tapete")
mp(A, "Cama casal", "160 × 200", cama(), -892, 487, 270, t3d="cama")
mp(A, "Criado-mudo", "40 × 40", criado(), -892, 445, 270, t3d="criado"); mp(A, "Criado-mudo", "40 × 40", criado(), -892, 650, 270, t3d="criado")
mp(A, "Guarda-roupa", "185 × 60", armario(185), -609, 405, 90, t3d="armario")
add(box_(-534, 405, 146, 95, ((-534, 500), (-388, 500))))                                          # banho 01
mp("BANHO 01", "Bacia", "40 × 65", vaso(), -453, 525, 90, tab=False, t3d="bacia")
mp("BANHO 01", "Bancada c/ cuba", "80 × 50", cuba_banho(80), -468, 642, 180, tab=False, t3d="bancada_banho")
A = "SUÍTE 02"
m(A, "Tapete", "220 × 130", [(R(-790, 120, 220, 130), "tapete")], tab=False, t3d="tapete")
mp(A, "Cama casal", "160 × 200", cama(), -757, 0, 0, t3d="cama")
mp(A, "Criado-mudo", "40 × 40", criado(), -802, 0, 0, t3d="criado"); mp(A, "Criado-mudo", "40 × 40", criado(), -592, 0, 0, t3d="criado")
mp(A, "Guarda-roupa", "160 × 60", armario(160), -892, 110, 270, t3d="armario")
m(A, "Escrivaninha", "120 × 50", [(R(-512, 75, 50, 120), "madeira")], t3d="escrivaninha", ang=90)
m(A, "Cadeira", "Ø 40", [(CI(-535, 135, 20), "cadeira")], t3d="cadeira_jantar", ang=270)
add(box_(-1157, 0, 80, 120, ((-1077, 0), (-1077, 120))))                                           # banho 02
mp("BANHO 02", "Bacia", "40 × 65", vaso(), -1065, 0, 0, tab=False, t3d="bacia")
mp("BANHO 02", "Bancada c/ cuba", "60 × 45", cuba_banho(60, 45), -1015, 75, 180, tab=False, t3d="bancada_banho")
add(box_(-1007, 135, 100, 140, ((-1007, 135), (-1007, 275))))                                      # banho master
mp("BANHO MASTER", "Bancada c/ cuba", "90 × 50", cuba_banho(90), -1157, 135, 0, tab=False, t3d="bancada_banho")
mp("BANHO MASTER", "Bacia", "40 × 65", vaso(), -1060, 210, 180, tab=False, t3d="bacia")
A = "SUÍTE MASTER"
m(A, "Tapete", "210 × 180", [(R(-1137, 440, 210, 180), "tapete")], tab=False, t3d="tapete")
mp(A, "Cama casal", "160 × 200", cama(), -1112, 492, 180, t3d="cama")
mp(A, "Criado-mudo", "40 × 40", criado(), -1157, 652, 180, t3d="criado"); mp(A, "Criado-mudo", "40 × 40", criado(), -947, 652, 180, t3d="criado")
m(A, "Banco (peseira)", "120 × 40", [(RR(-1092, 445, 120, 40, 4), "estofado2")], t3d="banco")
mp(A, "Rack + TV", "130 × 35", rack(130, 35), -1135, 290, 0, t3d="rack_tv")
A = "CLOSET MASTER"
mp(A, "Armário", "343 × 60", armario(343), -1362, 195, 270, t3d="armario"); mp(A, "Armário", "130 × 60", armario(130), -1302, 478, 180, t3d="armario")
m(A, "Puff", "Ø 50", [(CI(-1237, 320, 25), "estofado2")], t3d="puff")
A = "BANHO LAZER"
mp(A, "Bancada c/ cuba", "70 × 45", cuba_banho(70, 45), -1340, 553, 0, tab=False, t3d="bancada_banho")
add(box_(-1262, 553, 90, 90, ((-1262, 553), (-1262, 643), (-1172, 643))))
mp(A, "Bacia", "40 × 65", vaso(), -1237, 645, 90, tab=False, t3d="bacia")
A = "ÁREA DE SERVIÇO"
mp(A, "Lavadora", "60 × 65", maquina(), -1250, 0, 0, t3d="lavadora"); mp(A, "Secadora", "60 × 65", maquina(), -1315, 0, 0, t3d="lavadora")
m(A, "Bancada", "120 × 60", [(R(-1440, 0, 120, 60), "bancada")], t3d="bancada")
mp(A, "Armário (rouparia / limpeza)", "210 × 45", armario(210, 45), -1390, 135, 180, t3d="armario")
m("SERVIÇO EXTERNO", "Tanque duplo (existente)", "120 × 60",
  [(C.TQ, "loucas"), (RR(-1430, 382, 46, 50, 4), "inox"), (RR(-1430, 438, 46, 50, 4), "inox")], t3d="tanque", ang=90)
A = "ÁREA GOURMET"
m(A, "Churrasqueira (existente)", "220 × 60", [(R(-2367, 100, 60, 220), "bancada"), (R(-2362, 150, 50, 120), "inox_escuro")], t3d="churrasqueira", ang=270)
mp(A, "Bancada c/ cooktop e cuba (travertino)", "320 × 60", bancada_coz(320, 60, cook=200, cuba=60), -2280, 0, 0, t3d="bancada_cozinha", cook=200, cuba=60)
m(A, "Frigobar", "60 × 60", [(R(-1955, 0, 60, 60), "inox")], t3d="frigobar")
mz = mesa(-2140, 175, 240, 100, 4, cab=True)
m(A, "Mesa de jantar (10 lugares)", "240 × 100", mz[-1:], t3d="mesa_jantar"); cadeiras(A, mz)
m(A, "Tapete", "210 × 210", [(R(-1790, 110, 210, 210), "tapete")], tab=False, t3d="tapete")
mp(A, "Sofá 3 lugares", "220 × 90", sofa(220, 90), -1800, 0, 0, t3d="sofa")
mp(A, "Poltrona", "78 × 82", sofa(78, 82), -1770, 250, 180, t3d="poltrona_lounge"); mp(A, "Poltrona", "78 × 82", sofa(78, 82), -1660, 250, 180, t3d="poltrona_lounge")
m(A, "Mesa de centro", "100 × 60", [(RR(-1735, 140, 100, 60, 6), "madeira")], t3d="mesa_centro")
A = "DECK / PISCINA"
for x in (-2250, -2165, -1890, -1805): mp(A, "Espreguiçadeira", "65 × 190", espreguicadeira(), x, 420, 0, t3d="espreguicadeira")
m(A, "Ombrelone", "Ø 170", [(CI(-2027, 515, 85), "guardasol")], t3d="ombrelone")
for y in range(650, 960, 75): m(A, "Arbusto", "Ø 48", arbusto(-2330, y, 24), tab=False, t3d="arbusto")
A = "JARDIM"
m(A, "Árvore", "Ø 190", arvore(-1560, 830, 95), tab=False, t3d="arvore"); m(A, "Árvore", "Ø 120", arvore(-1625, 520, 60), tab=False, t3d="arvore")
for x in range(-1680, -1400, 56): m(A, "Pisante", "42 × 60", [(RR(x, 605, 42, 60, 8), "pedra")], tab=False, t3d="pisante")
for x in range(-1330, 560, 110): m("CORREDOR LATERAL", "Arbusto", "Ø 36", arbusto(x, 967, 18), tab=False, t3d="arbusto")
mp("GARAGEM", "Vaga de automóvel", "250 × 470", carro(), 620, 762, 90, t3d="carro")
A = "JARDIM FRONTAL"
m(A, "Árvore", "Ø 150", arvore(1085, 120, 75), tab=False, t3d="arvore"); m(A, "Árvore", "Ø 124", arvore(1085, 420, 62), tab=False, t3d="arvore")
for y in (250, 300, 520, 720): m(A, "Arbusto", "Ø 40", arbusto(1130, y, 20), tab=False, t3d="arbusto")
m("ACESSO COBERTO", "Vaso com planta", "Ø 60", vaso_planta(960, 40, 30), t3d="planta_grande"); m("ACESSO COBERTO", "Vaso com planta", "Ø 52", vaso_planta(960, 520, 26), t3d="planta_pequena")

def quadro_mobiliario():
    # [(ambiente, item, dimensao, quantidade)] na ordem em que aparecem
    out = []
    for amb, item, dim in MOB:
        for row in out:
            if row[:3] == [amb, item, dim]: row[3] += 1; break
        else: out.append([amb, item, dim, 1])
    return out

# ---------------- rotulos ----------------
NOMES = {   # nome no CAD (chave de P.ROOMS) -> (rotulo com acento, posicao)
    "ESTAR (PE-DIREITO DUPLO)": ("ESTAR", (330, 340)),
    "SALA DE TV": ("SALA DE TV", (-95, 345)),
    "JANTAR / COZINHA": ("JANTAR / COZINHA", (150, 125)),
    "LAVABO": ("LAVABO", (-300, 565)),
    "JARDIM DE INVERNO": ("JARDIM DE INVERNO", (-342, 45)),
    "CORREDOR 100": ("CIRCULAÇÃO", (-760, 340)),
    "SUITE 1": ("SUÍTE 1", (-780, 440)),
    "BANHO SUITE 1": ("BANHO", (-480, 585)),
    "SUITE 2": ("SUÍTE 2", (-680, 235)),
    "BANHO SUITE 2": ("BANHO", (-1117, 60)),
    "BANHO MASTER": ("BANHO MASTER", (-1040, 200)),
    "SUITE MASTER": ("SUÍTE MASTER", (-1032, 395)),
    "CLOSET MASTER": ("CLOSET", (-1237, 400)),
    "BANHO LAZER": ("BANHO LAZER", (-1300, 625)),
    "AREA DE SERVICO COBERTA": ("SERVIÇO", (-1350, 100)),
    "AREA DE SERVICO DESCOBERTA": ("SERVIÇO EXT.", (-1444, 290)),
    "GOURMET": ("ESPAÇO GOURMET", (-1890, 100)),
}
EXTERNOS_NOMES = [
    ("PISCINA 6,00 × 3,00", (-1980, 770)), ("DECK", (-2000, 951)), ("JARDIM", (-1520, 690)),
    ("GARAGEM", (840, 735)), ("ACESSO COBERTO", (845, 300)), ("JARDIM FRONTAL", (1085, 230)),
    ("RECUO", (637, 140)), ("ENTRADA", (845, 617)), ("CORREDOR LATERAL", (-300, 845)),
]
