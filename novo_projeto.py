# Cria a pasta de um cliente novo com a biblioteca do processo. Uso: py novo_projeto.py <Cliente> [pasta_base]
# Resultado: <pasta_base>\<Cliente>\scripts\ (gcad, prancha, modelos3d, gera_3d) e apresentacao-3d\modelo.html.
# Os modulos do levantamento, propostas, layout e prancha do cliente sao escritos durante o trabalho
# (use exemplo-narcelia\scripts como referencia: frontal.py, proposta04.py, layout04.py, prancha04.py, exporta_3d.py).
import os, sys, shutil

AQUI = os.path.dirname(os.path.abspath(__file__))
if len(sys.argv) < 2: sys.exit("uso: py novo_projeto.py <Cliente> [pasta_base]  (padrao: C:\\Dev\\CAD)")
cliente = sys.argv[1]; base = sys.argv[2] if len(sys.argv) > 2 else r"C:\Dev\CAD"
raiz = os.path.join(base, cliente)
if os.path.exists(raiz): sys.exit(f"ja existe: {raiz} (nada foi alterado)")
os.makedirs(os.path.join(raiz, "scripts")); os.makedirs(os.path.join(raiz, "apresentacao-3d"))
for f in ("gcad.py", "prancha.py", "modelos3d.py", "gera_3d.py"):
    shutil.copy2(os.path.join(AQUI, "biblioteca", f), os.path.join(raiz, "scripts", f))
for f in ("modelo.html", "CREDITOS.md"):        # modelo da pagina 3D: ajustar FICHAS e IDS para as propostas do cliente
    shutil.copy2(os.path.join(AQUI, "exemplo-narcelia", "apresentacao-3d", f), os.path.join(raiz, "apresentacao-3d", f))
print(f"ok -> {raiz}")
print("proximos passos: copie o croqui para a pasta, abra o GstarCAD 2022 LT e, no Claude Code, peca 'desenhar o levantamento'.")
