# Processo completo: do levantamento à proposta apresentada

Este é o roteiro que usamos para transformar um levantamento feito à mão em propostas de reforma. As propostas são desenhadas no GstarCAD, viram prancha padrão em PDF e uma maquete 3D na web. O caso real da cliente Narcelia está em `exemplo-narcelia/` e serve de referência para cada etapa.

O trabalho é feito com o **Claude Code**, que escreve e roda os scripts, junto com o arquiteto, que acompanha o GstarCAD aberto e corrige. Todas as medidas ficam em **scripts Python**, que são a fonte da verdade. O DWG é sempre gerado a partir deles.

```
croqui + fotos/vídeos
        │  (1) levantamento ─────────────► <Cliente> - Levantamento.dwg
        ▼
  módulos de geometria (frontal.py, fundos1.py, ...)
        │  (2) propostas ────────────────► <Cliente> - Proposta NN.dwg  + PROPOSTA-NN-MEMORIAL.md
        ▼
  propostaNN.py (ambientes, vãos, esquadrias, portas)
        │  (3) layout ───────────────────► <Cliente> - Proposta NN - Layout.dwg
        ▼
  layoutNN.py (mobiliário com ambiente, item, dimensão, tipo 3D, giro)
        ├─ (4) prancha padrão ───────────► <Cliente> - Proposta NN - Prancha Layout.pdf  (A1/A0, 1:50)
        └─ (5) maquete 3D web ───────────► apresentacao-3d/casa-<cliente>-3d.html (publicada como Artifact)
```

---

## 0. Preparação do projeto
1. Rode `py novo_projeto.py <Cliente>`. Ele cria `C:\Dev\CAD\<Cliente>\` com `scripts\` (biblioteca copiada) e `apresentacao-3d\`.
2. Coloque o croqui escaneado (PDF), as fotos e os vídeos da vistoria na pasta do cliente.
3. Abra o GstarCAD **2022 LT**. O 2024 instalado no escritório não tem executável utilizável. Deixe-o visível no segundo monitor, porque o arquiteto acompanha o desenho ao vivo.
4. No Claude Code, aberto na pasta `C:\Dev\CAD\<Cliente>`, peça: *"desenhar o levantamento do croqui"*. A skill `levantamento-cad` assume o roteiro.

## 1. Levantamento (croqui → DWG)
Detalhes em `docs/LEVANTAMENTO-CAMPO.md` e `docs/CHECKLIST-CAMPO.md`.

**Convenções:**
- **Medidas:** em cm. As cotas do croqui são **internas** (de face a face de parede). Parede de 15 cm, salvo indicação.
- **Referencial da folha:** x cresce em direção à rua e y cresce da divisa do fundo para o corredor lateral. No CAD vale `X = -x` (giro de 180°, ver `gcad.cad()`).
- **Módulos:** um módulo por folha ou casa do croqui, como `frontal.py` e `fundos1.py`. Cada um tem `ROOMS`, `OPENINGS`, `WINDOWS`, `DOORS` e `NOTES` como geometrias **shapely**. As paredes saem por cálculo: `buffer` dos ambientes menos ambientes, vãos e janelas.
- **Desenho:** os `desenha_*.py` limpam o desenho e redesenham tudo por COM (`Gcad.Application`, pywin32).

**Regras que evitam retrabalho:**
- **Somar as cadeias de cotas** antes de desenhar. O croqui raramente fecha, e as perguntas mais valiosas ao arquiteto são sobre as somas que não batem.
- Folha com números de cabeça para baixo indica que ela está **girada**.
- Peitoril alto (150 cm ou mais) indica banheiro.
- Se o arquiteto editou direto no GstarCAD, **leia o DWG antes de redesenhar** (`skill/levantamento-cad/scripts/ferramentas.py dump`). Incorpore as mudanças nos scripts com medidas arredondadas, porque o redesenho apaga tudo.
- Marque como `A CONFERIR` o que for estimado e pergunte ao arquiteto as dúvidas antes de desenhar.

## 2. Propostas (uma versão por arquivo)
Cada proposta nova é uma **cópia do DWG anterior** com scripts próprios. A versão anterior nunca é sobrescrita.

| Arquivo | Conteúdo |
|---|---|
| `propostaNN.py` | `ROOMS` (ambientes da proposta, montados com `R[...]` do existente e retângulos), `OPENINGS`, `WINDOWS`, `DOORS`, `CORRER`, piscina, cobertura, `NOTAS` |
| `desenha_propostaNN.py` | `assert G.doc.Name == "<Cliente> - Proposta NN.dwg"`: só desenha no arquivo certo |
| `PROPOSTA-NN-MEMORIAL.md` | o que muda em relação à anterior, áreas, quantitativo, observações técnicas, pendências |

- **Demolir e construir:** são calculados sozinhos, comparando as paredes do existente com as da proposta (`paredes()`). Na saída: branco = manter, amarelo tracejado = demolir, vermelho hachurado = construir.
- **Marcações do arquiteto:** ele marca as ideias por cima de um print. Convenção de cores: **vermelho** = fechar ou construir parede, **verde** = porta ou abertura, **amarelo** = demolir ou incorporar, **azul** = ambiente. Confirme as interpretações ambíguas e liste-as no memorial.
- **Critério padrão:** menor intervenção que atenda o programa.

Para criar a próxima versão, copie o `.dwg`, abra a cópia no GstarCAD, crie `propostaNN.py` a partir do anterior e rode `py desenha_propostaNN.py`.

## 3. Layout (mobiliário)
Arquivo `layoutNN.py` (ver `exemplo-narcelia/scripts/layout04.py`).
- **Peças:** cada peça tem coordenadas locais, com largura em x e as **costas em y = 0**. Exemplos: `cama()`, `sofa()`, `armario()`, `bancada_coz()`, `vaso()`, `cuba_banho()`, `mesa()`, `carro()`.
- **Giro:** `poe(pecas, x0, y0, ang)` gira a peça e a encosta num canto. `ang` vale 0 para as costas em y menor, 180 para y maior, 90 para x maior e 270 para x menor.
- **Registro:** `m(ambiente, item, dimensao, pecas, tab=True, t3d=None, ang=0, **params)` desenha a peça e registra no quadro de mobiliário. Com `t3d`, a peça também entra na maquete 3D. `mp(...)` é igual, com o `poe()` embutido, o que garante o mesmo giro na planta e no 3D.
- **Fora do quadro:** louças, boxes, tapetes e vegetação usam `tab=False`.
- **DWG:** `desenha_layoutNN.py` gera o `<Cliente> - Proposta NN - Layout.dwg`, com camadas `LAY-MOBILIARIO`, `LAY-LOUCAS`, `LAY-VEGETACAO` e outras.

## 4. Prancha padrão "PROPOSTA DE LAYOUT"
Padrão do escritório descrito em `docs/PADRAO-PRANCHA.md`. A biblioteca é `prancha.py`, e cada proposta tem seu `pranchaNN.py`, que é só configuração:
- **Pisos:** `piso_de(nome)` define o material de cada ambiente (porc90, porc60, deck, drenante, pedra, gramado, pedrisco, piscina).
- **Áreas externas:** o dicionário `EXT` traz as geometrias do quadro de áreas, e `POS_EXT` as posições dos rótulos.
- **Cotas:** são automáticas para os ambientes retangulares, com cadeias externas e chamadas a partir do lote.
- **Diagramação:** a folha é A1 deitada quando a casa é comprida. Use A0 em pé, como o modelo original, quando a casa for larga.
- **Carimbo:** projeto, cliente, data, folha e observações.

Para gerar: `py pranchaNN.py`. O resultado é o PDF vetorial (texto e cotas em Arial), com a planta humanizada em raster de 300 dpi.

A planta humanizada avulsa (PNG/PDF) sai com `humanizadaNN.py` e é opcional, porque a prancha já a contém.

## 5. Maquete 3D web
| Passo | Comando | O que faz |
|---|---|---|
| 1 | `py modelos3d.py` | Baixa do **Poly Haven** (CC0) os modelos e texturas do catálogo. Converte para GLB leve (WebP 512 px) com `npx @gltf-transform/cli`. Só é preciso rodar uma vez por máquina ou ao mudar o catálogo. |
| 2 | `py gera_3d.py` | Roda `exporta_3d.py` (cenas: existente + propostas), embute dados, modelos e texturas no HTML e grava `apresentacao-3d/casa-<cliente>-3d.html` |
| 3 | testar | `py -m http.server 8765` dentro de `apresentacao-3d/` e abrir num **iframe `sandbox="allow-scripts"`** (ver abaixo) |
| 4 | publicar | Pedir ao Claude Code para publicar o HTML como **Artifact**, sempre no mesmo link. **Só o HTML, sem arquivos de apoio.** |

- **Modelo da página:** `apresentacao-3d/modelo.html` é o modelo, com os marcadores `__DADOS__` e `__ASSETS__`.
- **Modo realista:** liga sozinho nas propostas que têm `layoutNN.py`, com pisos com textura, céu procedural e móveis reais. As outras propostas continuam como volumes de estudo.
- **Catálogo `CAT`:** liga o tipo `t3d` a um GLB do Poly Haven. Há dois modos de encaixe: `uniforme`, que mantém a proporção dentro da pegada, e `esticar`, que ajusta à pegada com a altura `h`. Use `giro` quando o modelo vier com a frente noutro eixo.
- **Construtores `B`:** modelam as peças sem equivalente contemporâneo no Poly Haven, como cama, sofá, armário, bancada, geladeira, louças, espreguiçadeira e árvores. Todos seguem a convenção local de largura em X, costas em −Z e base em y = 0.
- **Tipo novo:** escolha o asset em polyhaven.com, acrescente-o em `MODELOS` (`modelos3d.py`) e em `CAT` (`modelo.html`), ou escreva um construtor em `B`. Depois use `t3d="tipo"` no layout.

> ⚠️ **Por que tudo vai embutido:** o Artifact roda num iframe de **origem nula**. Toda imagem ou arquivo buscado por URL é bloqueado por CORS e o material fica **preto**. Por isso `gera_3d.py` embute tudo, até o limite de cerca de 15,5 MB, e a iluminação é procedural, sem HDRI. Sempre teste num iframe `sandbox="allow-scripts"` antes de publicar.

## 6. Entrega para o cliente (checklist)
- [ ] DWG da proposta (demolir/construir) e DWG de layout salvos
- [ ] `PROPOSTA-NN-MEMORIAL.md` com pendências e interpretações confirmadas
- [ ] Prancha PDF conferida: cotas legíveis, quadros batendo com a planta, carimbo preenchido
- [ ] 3D testado em iframe sandbox, sem erro no console e sem material preto
- [ ] Artifact republicado no **mesmo link** e compartilhado pelo menu Compartilhar, porque nasce privado

## 7. Problemas conhecidos
| Sintoma | Causa e solução |
|---|---|
| 3D publicado com texturas e móveis pretos | Arquivo buscado por URL dentro do iframe de origem nula. Rode `gera_3d.py`, que embute tudo, e publique só o HTML. |
| Acentos trocados (`Ã©`) na prévia local | O HTML é um fragmento sem `charset`, e o `http.server` não envia o charset. Na publicação a codificação fica certa. |
| `desenha_*.py` falha com `assert` | O documento ativo no GstarCAD não é o da proposta. Ative o arquivo certo; a trava existe para proteger as outras versões. |
| Edições manuais sumiram do DWG | O redesenho apaga tudo. Antes de rodar, leia o DWG com `ferramentas.py dump` e passe as mudanças para os scripts. |
| PNG não regrava (`Errno 22`) | O arquivo está aberto num visualizador. Feche-o e rode de novo. |
| GLB/HDR recusados na publicação | O Artifact não serve esses tipos, e nem precisa, porque `gera_3d.py` embute tudo. |
