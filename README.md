# Levantamento → Propostas (GstarCAD + Python + Claude Code)

Processo do escritório para transformar um **levantamento feito à mão** (croqui, fotos, vídeos) em:

1. planta do existente no **GstarCAD**, desenhada ao vivo via automação COM;
2. **propostas de reforma** versionadas, com demolir/construir calculados e memorial;
3. **planta de layout** com mobiliário (DWG);
4. **prancha padrão "PROPOSTA DE LAYOUT"** em PDF 1:50: planta humanizada, cotas, quadro de áreas, quadro de mobiliário e carimbo;
5. **maquete 3D web** interativa, com móveis reais (CC0) e cena realista, publicada como link.

Tudo nasce de scripts Python: as medidas ficam em código, e o DWG, o PDF e o 3D são gerados a partir delas. O trabalho é conduzido no **Claude Code** com a skill `levantamento-cad`, enquanto o arquiteto acompanha o GstarCAD e corrige.

## Começar
1. Instale: [`docs/INSTALACAO.md`](docs/INSTALACAO.md), ou só `powershell -ExecutionPolicy Bypass -File .\instalar.ps1`.
2. Leia o passo a passo: [`docs/PROCESSO.md`](docs/PROCESSO.md).
3. Novo cliente: `py novo_projeto.py <Cliente>` cria `C:\Dev\CAD\<Cliente>\` com a biblioteca.
4. Use o caso real como referência: [`exemplo-narcelia/`](exemplo-narcelia/), com o levantamento, as quatro propostas, o layout, a prancha e o 3D (só os scripts).

## Estrutura
| Pasta | Conteúdo |
|---|---|
| `biblioteca/` | Código genérico: `gcad.py` (COM do GstarCAD), `prancha.py` (prancha padrão), `modelos3d.py` (assets CC0 do Poly Haven), `gera_3d.py` (monta a página 3D com tudo embutido) |
| `skill/levantamento-cad/` | Skill do Claude Code: roteiro, `motor.py`, `analise.py`, `ferramentas.py` (dump do DWG), referências |
| `exemplo-narcelia/scripts/` | Caso completo: módulos do existente, `propostaNN.py`, `desenha_*.py`, `layout04.py`, `prancha04.py`, `humanizada04.py`, `exporta_3d.py` |
| `exemplo-narcelia/apresentacao-3d/` | `modelo.html` (página 3D com os marcadores `__DADOS__`/`__ASSETS__`) e créditos dos assets |
| `docs/` | Processo, instalação, padrão de prancha, levantamento de campo e checklist |

## Regras de ouro
- **Cada proposta nova é uma cópia** do DWG anterior com scripts próprios. Nunca se sobrescreve uma versão; os `desenha_*.py` checam o nome do documento ativo.
- **Antes de redesenhar, leia o DWG**, porque o arquiteto pode ter editado à mão e o redesenho apaga tudo.
- **Cotas do croqui são internas**, e as paredes têm 15 cm. Some as cadeias de cotas e pergunte o que não fecha.
- **3D:** publique **só o HTML** gerado por `gera_3d.py`. Arquivos à parte ficam pretos no link publicado (bloqueio de CORS).
- Fora do Git: croquis, fotos, vídeos, DWG e PDFs de clientes, que ficam na pasta do cliente em `C:\Dev\CAD\`.

## Licenças dos assets 3D
Modelos e texturas vêm do [Poly Haven](https://polyhaven.com) (**CC0**, domínio público). O carro é o "Car Concept" dos [glTF Sample Assets da Khronos](https://github.com/KhronosGroup/glTF-Sample-Assets/tree/main/Models/CarConcept) (**CC BY 4.0**, crédito obrigatório, já exibido na página 3D). São baixados por `modelos3d.py` e não ficam no repositório. Os demais móveis são modelados no próprio `modelo.html`.
