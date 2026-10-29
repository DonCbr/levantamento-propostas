# Exemplo: caso Narcelia (só os scripts)

Caso real usado para montar o processo: um lote de 10,12 × 35,54 m com cinco unidades, transformado em casa única com três suítes, área gourmet e piscina. Os arquivos da cliente (croqui, vídeos, DWG e PDFs) **não** estão aqui. Os scripts bastam para reproduzir as saídas.

| Etapa | Scripts | Saída |
|---|---|---|
| Levantamento | `frontal.py`, `entrada.py`, `fundos1.py`, `fundos2.py`, `fundos3.py` + `desenha_tudo.py`, `desenha_entrada.py` | `Narcelia - Levantamento.dwg` |
| Propostas 01 a 04 | `proposta.py`, `proposta02.py` … `proposta04.py` + `desenha_proposta*.py` | `Narcelia - Proposta NN.dwg` |
| Layout da P04 | `layout04.py` + `desenha_layout04.py` | `Narcelia - Proposta 04 - Layout.dwg` |
| Prancha padrão | `prancha04.py` (usa `prancha.py`) | `Narcelia - Proposta 04 - Prancha Layout.pdf` |
| Humanizada avulsa | `humanizada04.py` | PNG + PDF |
| 3D web | `exporta_3d.py`, `modelos3d.py`, `gera_3d.py` + `../apresentacao-3d/modelo.html` | `apresentacao-3d/casa-exemplo-narcelia-3d.html` |

## Rodar sem o GstarCAD
```powershell
cd scripts
py prancha04.py     # PDF da prancha na pasta exemplo-narcelia\
py modelos3d.py     # baixa os modelos e texturas CC0 (uma vez)
py gera_3d.py       # pagina 3D em ..\apresentacao-3d\
```

## Rodar com o GstarCAD
Abra (ou crie) no GstarCAD o DWG com o nome exato que o script espera, por exemplo `Narcelia - Proposta 04.dwg`, e rode o `desenha_*.py` correspondente. O script se recusa a desenhar em outro arquivo.
