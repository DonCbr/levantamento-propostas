# Ferramentas de apoio do levantamento.
#   py -I ferramentas.py pdf  <croqui.pdf> <pasta_saida>                 -> uma PNG por folha (200 dpi)
#   py -I ferramentas.py zoom <croqui.pdf> <folha(1..)> <saida.png> x0 y0 x1 y1  (coords 0..2000 x 0..1414)
#   py    ferramentas.py dump <saida.json>                                -> entidades do DWG aberto (referencial da folha)
#   py    ferramentas.py tela <saida.png>                                 -> captura do monitor onde o GstarCAD esta
# Folhas de contato de video (ffmpeg):
#   ffmpeg -i video.mp4 -vf "fps=1/3,scale=480:-1,tile=4x4" saida_%02d.jpg
import sys, json, os

def pdf(arq, saida):
    import pymupdf
    for i, p in enumerate(pymupdf.open(arq)):
        p.get_pixmap(dpi=200).save(os.path.join(saida, f"folha{i+1}.png"))

def zoom(arq, folha, saida, x0, y0, x1, y1):
    import pymupdf
    p = pymupdf.open(arq)[int(folha) - 1]; W, H = p.rect.width, p.rect.height
    clip = pymupdf.Rect(W*float(x0)/2000, H*float(y0)/1414, W*float(x1)/2000, H*float(y1)/1414)
    p.get_pixmap(dpi=300, clip=clip).save(saida)

def dump(saida):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import gcad as G
    f = lambda p: [round(-p[0], 1), round(p[1], 1)]
    out = []
    for i in range(G.ms.Count):
        e = G.ms.Item(i); d = {"t": e.ObjectName, "layer": e.Layer}
        if e.ObjectName == "AcDbLine": d["c"] = [f(e.StartPoint), f(e.EndPoint)]
        elif e.ObjectName == "AcDbPolyline":
            c = list(e.Coordinates); d["c"] = [f(c[k:k+2]) for k in range(0, len(c), 2)]
        elif e.ObjectName == "AcDbText": d["s"] = e.TextString; d["c"] = [f(e.InsertionPoint)]
        out.append(d)
    json.dump({"salvo": G.doc.Saved, "entidades": out}, open(saida, "w"), indent=0)
    print("salvo:", G.doc.Saved, "| entidades:", len(out))

def tela(saida):
    import subprocess
    ps = ("Add-Type -AssemblyName System.Windows.Forms,System.Drawing;"
          "$p=Get-Process gcad|?{$_.MainWindowHandle -ne 0}|select -First 1;"
          "$s=[System.Windows.Forms.Screen]::FromHandle($p.MainWindowHandle).Bounds;"
          "$b=New-Object System.Drawing.Bitmap $s.Width,$s.Height;"
          "[System.Drawing.Graphics]::FromImage($b).CopyFromScreen($s.Location,[System.Drawing.Point]::Empty,$s.Size);"
          f"$b.Save('{saida}')")
    subprocess.run(["powershell", "-NoProfile", "-Command", ps], check=True)

if __name__ == "__main__":
    cmd, *args = sys.argv[1:]
    {"pdf": pdf, "zoom": zoom, "dump": dump, "tela": tela}[cmd](*args)
