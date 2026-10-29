# Prancha "PROPOSTA DE LAYOUT" da Proposta 04 no padrao do escritorio (ver prancha.py). Uso: py prancha04.py
# A1 deitado (a casa e comprida): planta 1:50 em cima; legenda, quadro de areas, quadro de mobiliario e carimbo embaixo.
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shapely.geometry import box
from shapely.ops import unary_union
import proposta04 as P, layout04 as Y, prancha as PR

R = lambda x0, y0, w, h: box(x0, y0, x0 + w, y0 + h)
PASTA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDA = os.path.join(PASTA, "Narcelia - Proposta 04 - Prancha Layout")

# ---------------- ambientes ----------------
INTERNAS = [("SALA DE ESTAR", "ESTAR (PE-DIREITO DUPLO)"), ("SALA DE TV", "SALA DE TV"), ("JANTAR / COZINHA", "JANTAR / COZINHA"),
            ("LAVABO", "LAVABO"), ("CIRCULAÇÃO", "CORREDOR 100"), ("SUÍTE 01", "SUITE 1"), ("BANHO 01", "BANHO SUITE 1"),
            ("SUÍTE 02", "SUITE 2"), ("BANHO 02", "BANHO SUITE 2"), ("SUÍTE MASTER", "SUITE MASTER"),
            ("CLOSET MASTER", "CLOSET MASTER"), ("BANHO MASTER", "BANHO MASTER"), ("BANHO LAZER", "BANHO LAZER"),
            ("ÁREA DE SERVIÇO", "AREA DE SERVICO COBERTA"), ("ÁREA GOURMET", "GOURMET")]
SECOS_MADEIRA = {"ESTAR (PE-DIREITO DUPLO)", "SALA DE TV", "SUITE 1", "SUITE 2", "SUITE MASTER", "CLOSET MASTER"}
MOLHADAS = {"LAVABO", "BANHO SUITE 1", "BANHO SUITE 2", "BANHO MASTER", "BANHO LAZER", "AREA DE SERVICO COBERTA"}
def piso_de(nome):
    if nome in MOLHADAS: return "porc60"
    if nome in SECOS_MADEIRA: return "madeira"
    return {"JARDIM DE INVERNO": "pedrisco", "AREA DE SERVICO DESCOBERTA": "drenante"}.get(nome, "porc90")

paredes = unary_union([P.paredes(P.ROOMS, P.OPENINGS, P.WINDOWS)] + P.EXTRA)
fechada = unary_union([P.ROOMS[k] for _, k in INTERNAS]).buffer(P.T, join_style="mitre")
aberto = unary_union([g.buffer(1) for k, g in P.OPENINGS.items() if "ABERTA" in k])
casa = unary_union(list(P.ROOMS.values())).buffer(P.T, join_style="mitre")

# ---------------- areas externas (quadro de areas + rotulos) ----------------
acesso_social = R(1001, 562, 156, 120); canteiro = R(-1377, 952, 1960, 30)
EXT = {
    "ACESSO COBERTO": R(687, 0, 314, 707),
    "ACESSO SOCIAL": acesso_social,
    "JARDIM FRONTAL": R(1001, 0, 156, 707).difference(acesso_social),
    "RECUO": R(587, 0, 100, 278),
    "GARAGEM": R(600, 707, 557, 275),
    "CORREDOR LATERAL": R(-1377, 707, 1977, 275).difference(canteiro),
    "CANTEIROS": canteiro,
    "DECK": R(-2367, 405, 670, 577).difference(P.PISCINA),
    "PISCINA": P.PISCINA,
    "JARDIM / GRAMADO": R(-1697, 405, 320, 577).difference(casa).difference(P.PISCINA),
    "JARDIM DE INVERNO": P.ROOMS["JARDIM DE INVERNO"],
    "SERVIÇO EXT. (DESCOB.)": P.ROOMS["AREA DE SERVICO DESCOBERTA"],
}
POS_EXT = {"ACESSO COBERTO": (845, 300), "ACESSO SOCIAL": (1079, 622), "JARDIM FRONTAL": (1079, 230), "RECUO": (637, 140),
           "GARAGEM": (840, 733), "CORREDOR LATERAL": (-300, 845), "DECK": (-2000, 951), "PISCINA": (-1980, 770),
           "JARDIM / GRAMADO": (-1530, 700), "JARDIM DE INVERNO": (-342, 45), "SERVIÇO EXT. (DESCOB.)": (-1444, 290)}
ROT_EXT = {"SERVIÇO EXT. (DESCOB.)": "SERVIÇO EXT.", "JARDIM / GRAMADO": "JARDIM"}

internas = [(rot, P.ROOMS[k].area / 1e4) for rot, k in INTERNAS]
externas = [(k, g.area / 1e4) for k, g in EXT.items()]
a_util = sum(a for _, a in internas); a_ext = sum(a for _, a in externas); a_fech = fechada.area / 1e4

POS = {k: pos for k, (_, pos) in Y.NOMES.items()}
POS["SUITE 2"] = (-680, 218)
rotulos = [(rot, P.ROOMS[k].area / 1e4, POS[k]) for rot, k in INTERNAS]
rotulos += [(ROT_EXT.get(k, k), EXT[k].area / 1e4, POS_EXT[k]) for k in POS_EXT]

# ---------------- cotas ----------------
def cotas(pr, pg):
    # internas: largura e profundidade de cada ambiente retangular (encostadas na parede do alto e da esquerda da vista)
    for nome, g in P.ROOMS.items():
        x0, y0, x1, y1 = g.bounds
        if abs(g.area - (x1 - x0) * (y1 - y0)) > 1 or nome == "CORREDOR 100": continue
        pr.cota(pg, (x0, y1 - 18), (x1, y1 - 18), 1); pr.cota(pg, (x1 - 18, y0), (x1 - 18, y1), 1)
    pr.cota(pg, (-223, 255), (572, 255), 1); pr.cota(pg, (552, 0), (552, 293), 1)      # jantar / cozinha (em L)
    pr.cota(pg, (-860, 290), (-860, 390), 1)                                             # circulacao de 1,00
    # externas: cadeia parcial + total, com linhas de chamada desde o lote
    X0, Y0, X1, Y1 = Y.LOTE.bounds
    baixo = [X0, -2367, -1527, -1512, -1172, -1157, -907, -892, -462, -447, -238, -223, 572, 587, 687, 1001, 1157, X1]
    alto = [X0, -1377, -1362, -1172, -1157, -907, -892, -549, -534, -388, -373, -223, -208, 87, 672, 687, X1]
    rua = [Y0, 0, 293, 692, 707, 982, Y1]; fundo = [Y0, 0, 390, 405, 982, Y1]
    for pts, fixo, hor, lado, borda in ((baixo, Y0 - 45, True, -1, Y0), (alto, Y1 + 45, True, 1, Y1),
                                        (rua, X1 + 45, False, 1, X1), (fundo, X0 - 45, False, -1, X0)):
        pr.cadeia(pg, pts, fixo, hor, lado)
        tot = fixo + (fixo - borda)                                                       # total, uma linha mais p/ fora
        a, b = ((pts[0], tot), (pts[-1], tot)) if hor else ((tot, pts[0]), (tot, pts[-1]))
        pr.cota(pg, a, b, lado, tam=6.4)
        for v in pts:                                                                      # linhas de chamada
            p, q = ((v, borda), (v, tot)) if hor else ((borda, v), (tot, v))
            pr.lin(pg, pr.mm(*p), pr.mm(*q), (0.92, 0.55, 0.55), 0.2)

# ---------------- blocos da folha ----------------
LEGENDA = ["parede", "madeira", "porc90", "porc60", "deck", "drenante", "pedra", "travertino",
           "piscina", "gramado", "pedrisco", "projecao", "esquadria"]
def blocos(pr, pg):
    y = pr.legenda(pg, 20, 278, LEGENDA, colunas=2, larg=110)
    pr.quadro_areas(pg, 20, y + 8, 225, internas, externas,
                    [("ÁREA ÚTIL INTERNA", a_util), ("ÁREA EXTERNA", a_ext), ("ÁREA CONSTRUÍDA (FECHADA)", a_fech)])
    pr.quadro_mobiliario(pg, 256, 272, 210, Y.quadro_mobiliario(),
                         "Dimensões em centímetros (comprimento × largura). Louças, boxes, tapetes e paisagismo indicativos.")
    pr.carimbo(pg, 478, 468, 826, 579, {
        "titulo": "PROPOSTA DE LAYOUT", "subtitulo": "RESIDÊNCIA UNIFAMILIAR – REFORMA",
        "projeto": "PROPOSTA 04 – REVISÃO DA PROPOSTA 02", "cliente": "NARCELIA",
        "conteudo": "PLANTA BAIXA – LAYOUT PROPOSTO", "escala": "1:50", "data": "29/10/2026", "folha": "01/01",
        "area_util": f"{a_util:.2f} m²".replace(".", ","), "area_construida": f"{a_fech:.2f} m²".replace(".", ","),
        "obs": ["Desenho ilustrativo para apresentação da proposta de layout.",
                "Cotas em metros; áreas úteis medidas pelas faces internas das paredes.",
                "Mobiliário, cores e revestimentos ilustrativos; medidas a conferir no local antes da execução.",
                "Estudo sobre levantamento; vistoria estrutural das paredes a demolir pendente."]})

CFG = {
    "escala": 50, "folha_mm": (841, 594), "planta_mm": ((841 - (Y.LOTE.bounds[2] - Y.LOTE.bounds[0]) * 10 / 50) / 2, 38),   # centrada
    "lote": Y.LOTE, "conteudo": "PLANTA BAIXA – LAYOUT PROPOSTO",
    "pisos_externos": [(Y.LOTE, "gramado"), (R(-1377, 707, 2534, 275), "drenante"), (EXT["ACESSO COBERTO"], "pedra"),
                       (acesso_social, "pedra"), (EXT["RECUO"], "deck"), (R(-2367, 405, 670, 577), "deck"),
                       (P.PISCINA, "pedra"), (P.PISCINA.buffer(-20, join_style="mitre"), "piscina"), (canteiro, "pedrisco")],
    "soleiras": casa.difference(aberto), "ambientes": P.ROOMS, "piso_de": piso_de,
    "pecas": Y.PECAS, "paredes": paredes, "muros": Y.MUROS, "gradil": Y.GRADIL,
    "janelas": P.WINDOWS, "portas": list(P.DOORS.values()), "correr": [P.OPENINGS[k] for k in P.CORRER],
    "projecao": [P.COBERTURA.intersection(Y.LOTE)], "rotulos": rotulos,
    "notas": [("PÉ-DIREITO DUPLO", (530, 470), 5.5)], "cotas": cotas, "blocos": blocos,
}

if __name__ == "__main__":
    PR.Prancha(CFG).gera(SAIDA + ".pdf")
    print(f"ok -> {SAIDA}.pdf | util {a_util:.2f} | externa {a_ext:.2f} | fechada {a_fech:.2f} | lote {Y.LOTE.area/1e4:.2f}")
