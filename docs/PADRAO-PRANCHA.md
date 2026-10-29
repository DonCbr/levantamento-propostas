# Padrão de prancha: "PROPOSTA DE LAYOUT"

Toda proposta apresentada ao cliente sai neste padrão, gerado por `prancha.py`. A referência de formato é a prancha de layout residencial usada pelo escritório, uma folha única em A0 em pé. O arquivo original fica fora deste repositório por conter dados de cliente.

## Conteúdo da folha
1. **Planta baixa humanizada 1:50:**
   - cores claras e lisas, só com a grade das placas: porcelanato 90×90 nas áreas secas, 60×60 nas molhadas;
   - deck com réguas, piso drenante, pedra natural, travertino nas bancadas, gramado com trama diagonal e pedrisco claro nos canteiros;
   - paredes em preto chapado e esquadrias em branco com eixo azul-claro;
   - sombra suave **só** em móveis e vegetação.
2. **Cotas vermelhas em metros** (`3,85`), de três tipos:
   - internas, com largura e profundidade de cada ambiente;
   - cadeias externas nos quatro lados com as paredes (`0,15`), mais o total;
   - linhas de chamada desde o lote.
3. **Rótulo de cada ambiente:** nome em negrito e área em m² logo abaixo, sem contorno.
4. **Título e legenda:** "PLANTA BAIXA – LAYOUT PROPOSTO" com a escala, e legenda de materiais com amostras, só dos materiais usados.
5. **Quadro de áreas:** áreas internas e externas em duas colunas, com os totais de área útil interna, área externa e área construída (fechada).
6. **Quadro de mobiliário:** ambiente (célula mesclada), item, dimensões em cm e quantidade, com nota de rodapé. Ele sai direto de `layoutNN.py`, pela função `m()`.
7. **Carimbo:**
   - "PROPOSTA DE LAYOUT" com o subtítulo;
   - projeto, cliente, conteúdo, escala, data e folha;
   - área útil interna, área construída (fechada) e observações numeradas.

## Diagramação
- **Casa comprida:** A1 deitado. Planta em cima; legenda, quadro de áreas, quadro de mobiliário e carimbo numa faixa embaixo (exemplo `prancha04.py`).
- **Casa larga:** A0 em pé, como o modelo original. Planta à esquerda, quadros na coluna da direita, legenda embaixo à esquerda e carimbo embaixo à direita.
- **Fonte:** Arial em todos os textos. A planta entra em raster de 300 dpi; texto, cotas e quadros são vetoriais.
- **Impressão:** em tamanho real, o PDF sai exatamente em 1:50.

## Observações padrão do carimbo
1. Desenho ilustrativo para apresentação da proposta de layout.
2. Cotas em metros; áreas úteis medidas pelas faces internas das paredes.
3. Mobiliário, cores e revestimentos ilustrativos; medidas a conferir no local antes da execução.
4. Observações específicas do estudo, como vistoria estrutural pendente.
