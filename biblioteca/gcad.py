# Helpers para desenhar no GstarCAD aberto via COM.
import time
import pythoncom
import win32com.client
from win32com.client import VARIANT

app = win32com.client.GetActiveObject("Gcad.Application")
doc = app.ActiveDocument
ms = doc.ModelSpace
PAUSA = 0.15

def cad(x, y):
    # referencial da folha -> CAD com giro de 180 graus
    return (-x, y)

def arr(vals):
    return VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, [float(v) for v in vals])

def pt(x, y):
    X, Y = cad(x, y)
    return arr([X, Y, 0])

def layer(name):
    doc.ActiveLayer = doc.Layers.Item(name)

def show(ent):
    ent.Update()
    time.sleep(PAUSA)
    return ent

def pline(coords, closed=True):
    flat = []
    for x, y in coords:
        flat += list(cad(x, y))
    p = ms.AddLightWeightPolyline(arr(flat))
    p.Closed = closed
    return show(p)

def line(a, b):
    return show(ms.AddLine(pt(*a), pt(*b)))

def arc(c, raio, a0, a1):
    return show(ms.AddArc(pt(*c), raio, a0, a1))

def text(s, x, y, h=12):
    t = ms.AddText(s, pt(x, y), h)
    return show(t)

def zoom():
    app.ZoomExtents()

def ensure_layer(name, color):
    try:
        return doc.Layers.Item(name)
    except Exception:
        l = doc.Layers.Add(name); l.Color = color; return l

def ctext(s, x, y, h=14):
    t = ms.AddText(s, pt(x, y), h)
    t.Alignment = 10            # meio-centro
    t.TextAlignmentPoint = pt(x, y)
    return show(t)

def dim(a, b, off, h=12):
    d = ms.AddDimAligned(pt(*a), pt(*b), pt(*off))
    d.TextHeight = h; d.ArrowheadSize = 8; d.ExtensionLineExtend = 5
    return show(d)

def clear():
    for i in range(ms.Count - 1, -1, -1):
        ms.Item(i).Delete()
