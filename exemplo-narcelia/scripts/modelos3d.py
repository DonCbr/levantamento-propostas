# Baixa e prepara os modelos e texturas (todos CC0, Poly Haven) usados no 3D web. Uso: py modelos3d.py
# Downloads ficam em apresentacao-3d/_cache/<id>/ (nao publicado); saidas em modelos/ (GLB) e texturas/ (JPG).
# A pagina publicada roda num iframe de origem nula: nada pode ser buscado por URL (CORS). Por isso gera_3d.py embute
# estes arquivos no proprio HTML; aqui eles saem leves (texturas dos GLB em WebP 512 px).
# Pecas sem equivalente contemporaneo no Poly Haven (camas, sofas, armarios, loucas, bancadas...) sao modeladas na pagina.
import json, os, subprocess, urllib.request, io
from PIL import Image

RAIZ = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "apresentacao-3d")
CACHE, MOD, TEX = (os.path.join(RAIZ, p) for p in ("_cache", "modelos", "texturas"))

MODELOS = {   # tipo do catalogo (layoutNN.py, t3d=...) -> asset
    "poltrona": "modern_arm_chair_01", "poltrona_lounge": "mid_century_lounge_chair",
    "mesa_centro": "modern_coffee_table_01", "mesa_centro_redonda": "coffee_table_round_01",
    "criado": "side_table_01", "cadeira_jantar": "dining_chair_02", "rack": "modern_wooden_cabinet",
    "planta_grande": "potted_plant_02", "planta_pequena": "potted_plant_04",
}
# Fora do Poly Haven (download direto, sem login). CC BY 4.0: exige credito (vai no CREDITOS.md e no rodape da pagina)
KHRONOS = {   # tipo -> (asset, url, credito)
    "carro": ("CarConcept", "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Assets/main/Models/CarConcept/glTF-Binary/CarConcept.glb",
              "Car Concept © 2024 Darmstadt Graphics Group GmbH, modelo e texturas de Eric Chadwick (Khronos glTF Sample Assets), CC BY 4.0"),
}
TEXTURAS = {  # nome na pagina -> asset (diffuse, normal GL, rugosidade em 1k)
    "deck": "wood_floor_deck", "grama": "leafy_grass", "pedrisco": "bicolour_gravel", "pavers": "concrete_pavers",
    "pedra": "marble_01", "tecido": "cotton_jersey", "tapete": "polar_fleece", "linho": "rough_linen",
    "madeira": "oak_veneer_01", "madeira_clara": "white_oak_veneer", "piso_madeira": "laminate_floor_02",
}
TAM_TEX = 512

def baixa(url):
    req = urllib.request.Request(url, headers={"User-Agent": "narcelia-3d (estudo de arquitetura)"})
    return urllib.request.urlopen(req, timeout=120).read()

def arquivos(asset): return json.loads(baixa(f"https://api.polyhaven.com/files/{asset}"))

def modelo(asset):
    destino = os.path.join(MOD, f"{asset}.glb")
    if os.path.exists(destino): return destino
    pasta = os.path.join(CACHE, asset); os.makedirs(pasta, exist_ok=True)
    g = arquivos(asset)["gltf"]["1k"]["gltf"]
    nome = os.path.join(pasta, os.path.basename(g["url"]))
    if not os.path.exists(nome):
        open(nome, "wb").write(baixa(g["url"]))
        for rel, f in g["include"].items():
            p = os.path.join(pasta, *rel.split("/")); os.makedirs(os.path.dirname(p), exist_ok=True)
            open(p, "wb").write(baixa(f["url"]))
    # GLB unico, texturas em WebP, sem compressao de malha (o three.js 0.128 le direto)
    cmd = ["npx", "-y", "@gltf-transform/cli@4", "optimize", nome, destino, "--compress", "false",
           "--texture-compress", "webp", "--texture-size", str(TAM_TEX), "--simplify", "false"]
    subprocess.run(cmd, check=True, shell=(os.name == "nt"), cwd=pasta, capture_output=True)
    return destino

def modelo_url(asset, url):
    # malha pesada: simplifica (35%) e quantiza os vertices (KHR_mesh_quantization, lido direto pelo three.js 0.128)
    destino = os.path.join(MOD, f"{asset}.glb")
    if os.path.exists(destino): return destino
    pasta = os.path.join(CACHE, asset); os.makedirs(pasta, exist_ok=True)
    orig = os.path.join(pasta, asset + ".glb")
    if not os.path.exists(orig): open(orig, "wb").write(baixa(url))
    cmd = ["npx", "-y", "@gltf-transform/cli@4", "optimize", orig, destino, "--compress", "quantize", "--texture-compress", "webp",
           "--texture-size", str(TAM_TEX), "--simplify", "true", "--simplify-ratio", "0.35", "--simplify-error", "0.0008"]
    subprocess.run(cmd, check=True, shell=(os.name == "nt"), cwd=pasta, capture_output=True)
    return destino

def textura(nome, asset):
    f = arquivos(asset); saidas = []
    for mapa, chave in (("diff", "Diffuse"), ("nor", "nor_gl"), ("rough", "Rough")):
        destino = os.path.join(TEX, f"{nome}_{mapa}.jpg"); saidas.append(destino)
        if os.path.exists(destino) or chave not in f: continue
        im = Image.open(io.BytesIO(baixa(f[chave]["1k"]["jpg"]["url"]))).convert("RGB")
        im.resize((TAM_TEX, TAM_TEX), Image.LANCZOS).save(destino, "JPEG", quality=80, optimize=True)
    return saidas

if __name__ == "__main__":
    for p in (CACHE, MOD, TEX): os.makedirs(p, exist_ok=True)
    creditos = ["# Créditos dos assets 3D", "", "Poly Haven: CC0 (domínio público), https://polyhaven.com. Khronos: CC BY 4.0 (crédito obrigatório).", ""]
    for tipo, asset in MODELOS.items():
        d = modelo(asset); print(f"modelo {tipo:20s} {asset:28s} {os.path.getsize(d) / 1e6:5.2f} MB", flush=True)
        creditos.append(f"- Modelo `{asset}` ({tipo}): https://polyhaven.com/a/{asset}")
    for tipo, (asset, url, credito) in KHRONOS.items():
        d = modelo_url(asset, url); print(f"modelo {tipo:20s} {asset:28s} {os.path.getsize(d) / 1e6:5.2f} MB", flush=True)
        creditos.append(f"- Modelo `{asset}` ({tipo}): {credito}. https://github.com/KhronosGroup/glTF-Sample-Assets/tree/main/Models/{asset}")
    for nome, asset in TEXTURAS.items():
        t = textura(nome, asset); print(f"textura {nome:20s} {asset:28s} {sum(os.path.getsize(x) for x in t if os.path.exists(x)) / 1e6:5.2f} MB", flush=True)
        creditos.append(f"- Textura `{asset}` ({nome}): https://polyhaven.com/a/{asset}")
    creditos.append("- Iluminação: céu procedural gerado na página (sem arquivo).")
    open(os.path.join(RAIZ, "CREDITOS.md"), "w", encoding="utf-8").write("\n".join(creditos) + "\n")
