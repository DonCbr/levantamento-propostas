# Instalação

Ambiente testado: **Windows 11**, com o GstarCAD aberto na mesma máquina.

## Atalho
Abra o PowerShell na pasta do repositório e rode:
```powershell
powershell -ExecutionPolicy Bypass -File .\instalar.ps1
```
O script faz quatro coisas:
- instala via `winget` o que faltar entre Python 3.14, Node.js LTS e Git;
- instala os pacotes Python;
- deixa em cache a ferramenta de GLB;
- copia a skill para o Claude Code.

No final, ele confere se o GstarCAD está registrado para automação.

## O que precisa existir

| Item | Versão usada | Para quê |
|---|---|---|
| **GstarCAD 2022 LT** | 2022 | Desenho ao vivo via COM (`Gcad.Application`). O 2024 do escritório não tem executável utilizável. |
| **Python** (launcher `py`) | 3.14 | Todos os scripts |
| pywin32 | 312 | Automação COM do GstarCAD |
| shapely | 2.2 | Geometria: ambientes, paredes por diferença, áreas |
| numpy | 2.5 | Texturas da planta humanizada |
| pillow | 13.0 | Imagens (planta, amostras da legenda, texturas) |
| pymupdf | 2.0 | PDF vetorial da prancha (texto e cotas em Arial) e leitura do croqui |
| **Node.js** (npx) | 24 LTS | `@gltf-transform/cli@4` (4.5) para otimizar os modelos 3D |
| **Claude Code** | atual | Execução do processo com a skill `levantamento-cad` |
| Playwright MCP (opcional) | `@playwright/mcp@latest` | Conferir a maquete no navegador antes de publicar |
| Fontes Arial e Bahnschrift | já vêm no Windows | Prancha e planta humanizada |

Os pacotes Python estão em `requirements.txt`:
```powershell
py -m pip install -r requirements.txt
```

## Skill do Claude Code
A pasta `skill/levantamento-cad/` vai para `%USERPROFILE%\.claude\skills\levantamento-cad\`. O `instalar.ps1` faz essa cópia. Com ela, o Claude Code reconhece pedidos como *"desenhar o levantamento"* e *"passar o croqui para o CAD"* e segue o roteiro do escritório.

Para conferir páginas no navegador (recomendado), instale o Playwright MCP:
```powershell
claude mcp add --scope user playwright -- cmd /c npx -y @playwright/mcp@latest
```
No Git Bash, use `MSYS_NO_PATHCONV=1` antes do comando, senão o `/c` vira `C:/`.

## Conferência rápida
```powershell
cd exemplo-narcelia\scripts
py prancha04.py      # gera a prancha PDF de exemplo (não precisa do GstarCAD)
py modelos3d.py      # baixa os modelos 3D (precisa de internet e Node)
py gera_3d.py        # gera a maquete 3D de exemplo
```
