# Monta a pagina do 3D web: exporta as cenas (exporta_3d.py) e embute dados + modelos + texturas no HTML.
# Uso: py gera_3d.py   ->  apresentacao-3d/casa-<cliente>-3d.html (publicar so esse arquivo, sem `files`)
# A pagina publicada roda num iframe de origem nula, onde buscar arquivos por URL e bloqueado (CORS) e as texturas
# ficariam pretas; por isso tudo vai embutido: texturas como data URI e glTF em JSON com o buffer em data URI.
import os, re, sys, json, base64, struct, subprocess, tempfile

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.join(os.path.dirname(AQUI), "apresentacao-3d")
LIMITE = 15.5e6                                               # pagina publicada: ate 16 MB

def gltf_json(glb):
    b = open(glb, "rb").read(); n = struct.unpack("<I", b[12:16])[0]
    j = json.loads(b[20:20 + n]); o = 20 + n; nb = struct.unpack("<I", b[o:o + 4])[0]; binario = b[o + 8:o + 8 + nb]
    j["buffers"] = [{"byteLength": len(binario), "uri": "data:application/octet-stream;base64," + base64.b64encode(binario).decode()}]
    return j

def assets(html):
    usados = set()
    for nome in re.findall(r'matTex\("([a-z_]+)"', html): usados |= {f"{nome}_diff", f"{nome}_nor", f"{nome}_rough"}
    usados |= set(re.findall(r'tex\("([a-z_]+)"', html))
    out = {}
    for t in sorted(usados):
        p = os.path.join(RAIZ, "texturas", t + ".jpg")
        if os.path.exists(p): out["texturas/" + t] = "data:image/jpeg;base64," + base64.b64encode(open(p, "rb").read()).decode()
    for m in sorted(set(re.findall(r'glb: "([A-Za-z0-9_]+)"', html))):
        out["modelos/" + m] = gltf_json(os.path.join(RAIZ, "modelos", m + ".glb"))
    return out

if __name__ == "__main__":
    tmp = os.path.join(tempfile.gettempdir(), "cenas_3d.json")
    subprocess.run([sys.executable, os.path.join(AQUI, "exporta_3d.py"), tmp], check=True)
    html = open(os.path.join(RAIZ, "modelo.html"), encoding="utf-8").read()
    A = assets(html)
    pagina = html.replace("__DADOS__", open(tmp, encoding="utf-8").read()).replace("__ASSETS__", json.dumps(A, separators=(",", ":")))
    cliente = os.path.basename(os.path.dirname(AQUI)).lower().replace(" ", "-")      # pasta do projeto (ex.: Narcelia)
    saida = os.path.join(RAIZ, f"casa-{cliente}-3d.html")
    open(saida, "w", encoding="utf-8").write(pagina)
    tam = os.path.getsize(saida)
    print(f"ok -> {saida} | {tam / 1e6:.2f} MB | {len(A)} assets embutidos")
    if tam > LIMITE: sys.exit(f"pagina acima do limite de publicacao ({tam / 1e6:.1f} MB)")
