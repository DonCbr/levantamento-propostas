---
name: levantamento-cad
description: Transforma um levantamento arquitetonico feito a mao (croqui escaneado em PDF, fotos/videos da vistoria) em planta baixa no GstarCAD, desenhando ao vivo por COM enquanto o arquiteto acompanha. Use quando o usuario pedir para "desenhar o levantamento", "passar o croqui para o CAD", "desenhar essa planta no GstarCAD/Gestarcad" ou iniciar um novo levantamento de cliente.
---

# Levantamento arquitetonico -> GstarCAD

Rascunho criado a partir do levantamento da cliente Narcelia (out/2026). Caso completo em
`referencias/caso-narcelia.md`; checklist de campo em `referencias/checklist-campo.md`.

## Preparacao
1. Criar a pasta do projeto: `C:\Dev\CAD\<Cliente>\` com `scripts\` e uma copia do croqui.
2. Abrir o GstarCAD visivel (o usuario quer acompanhar): `New-Object -ComObject Gcad.Application`,
   `Visible = $true`, novo documento, e salvar ja como `<Cliente> - Levantamento.dwg` na pasta.
3. Copiar `scripts/gcad.py` para `<projeto>\scripts\`. Dependencias: `py -m pip install shapely pywin32 pymupdf`.
4. Renderizar o croqui: `py -I scripts/ferramentas.py pdf <croqui.pdf> <scratchpad>`; ampliar trechos com `zoom`.
5. Videos: folhas de contato com ffmpeg (ver `ferramentas.py`). Nao ha audio na analise: perguntar se algo foi falado.

## Perguntas iniciais (uma rodada, so o que muda o desenho)
- Cotas internas ou externas? Espessura de parede (padrao 15)?
- Por qual folha comecar (a mais completa)? Orientacao (numeros de cabeca para baixo = folha girada)?
- Como as folhas se ligam (sequencia rua -> fundo)?

## Modelagem (um modulo .py por folha/casa)
Referencial da folha em cm: x para a rua, y da divisa do fundo para o corredor; no CAD X = -x, Y = y.
Cada modulo define `ROOMS`, `OPENINGS`, `WINDOWS`, `DOORS` e opcionalmente `MERGE`, `LOUCAS`, `NOTES`,
`LINES`, `EXTRA_WALL` (formato no cabecalho de `scripts/motor.py`). Regras:
- Paredes nao sao desenhadas a mao: saem de `pegada - comodos - vaos` (`motor.paredes`).
- Posicoes derivadas de constantes nomeadas (ex.: `X_BD`, `Y_CORR`), nunca numeros soltos repetidos.
- Boneca padrao 5 cm (`BON`); excecoes como constantes proprias.
- Item estimado -> nota com "A CONFERIR" (vai para a camada ARQ-CONFERIR).
- Antes de desenhar uma folha: **somar as cadeias de cotas em codigo** e perguntar sobre o que nao fecha,
  oferecendo opcoes concretas (ex.: "confiar no lado do corredor" x "lado da divisa").

## Ciclo de desenho
`py scripts/motor.py <projeto\scripts> modulo1 modulo2 ...` redesenha tudo (apaga o desenho!).
1. Desenhar, capturar a tela (`ferramentas.py tela`) e conferir a imagem antes de relatar.
2. Salvar (`G.doc.Save()`) depois de cada etapa.
3. **Se o usuario editou no CAD**: `ferramentas.py dump`, comparar com o modelo, traduzir as mudancas
   para os modulos com medidas arredondadas, confirmar as ambiguas e so entao redesenhar.

## Fechamento
- `py scripts/analise.py <projeto\scripts> modulos...`: paredes fora do padrao, sobreposicoes,
  portas batendo, unidades e acessos (unidades x numero de medidores), unidades sem banheiro,
  comodos sem janela, area total.
- Relatorio de inconsistencias: divergencias croqui x desenho (tabela), estimados, faltantes.
- Atualizar a memoria do projeto com decisoes e pendencias.

## Licoes do caso Narcelia
- Croqui raramente fecha: as perguntas mais valiosas foram sobre somas que nao batiam.
- Videos confirmam usos, degraus, entradas e numero de unidades, mas nao medidas.
- Peitoril alto (>=150) indica banheiro; numeros invertidos indicam folha girada.
- Contas de comprimento disponivel sempre em codigo (errei uma de cabeca).

## Entrega das propostas: prancha padrao "PROPOSTA DE LAYOUT"
Toda proposta para o cliente sai no padrao do modelo `C:\Dev\CAD\Modelos\PROPOSTA_ELAINE_R03_PROPOSTA.pdf`:
planta humanizada 1:50 (cores claras, so a grade das placas, sombra so em moveis/vegetacao), cotas vermelhas
em metros (internas por ambiente + cadeias externas com total), nome + area em cada ambiente, legenda de
materiais, quadro de areas (internas, externas, util interna, externa, construida fechada), quadro de
mobiliario (ambiente, item, dim. cm, qtd.) e carimbo (projeto, cliente, conteudo, escala, data, folha, areas, obs.).
- Biblioteca: `scripts/prancha.py` (generica; copiar p/ `<projeto>\scripts\`). Precisa de pymupdf, PIL, numpy, shapely.
- Por proposta: `layoutNN.py` (mobiliario com `m(ambiente, item, dim, pecas)`) + `pranchaNN.py` (config: pisos por
  ambiente, areas externas, rotulos, cotas, diagramacao). Caso pronto: Narcelia, `prancha04.py`.
- Folha: escolher pelo formato da planta (casa comprida -> A1 deitado, planta em cima e quadros embaixo; casa larga
  -> folha em pe como o modelo, quadros na coluna da direita).
