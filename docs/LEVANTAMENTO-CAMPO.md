# Processo do levantamento — Narcelia (out/2026)

Registro de como o levantamento foi feito, para virar a skill `levantamento-cad`.

## Entradas
- Croqui à mão escaneado em PDF (`Croqui levantamento.pdf`, 4 folhas: Entrada, Casa Frontal, Fundos 1, folha 4).
- 4 vídeos da vistoria (WhatsApp, sem medidas, ~6 min). Úteis para usos, louças, portas, degraus, coberturas, medidores.
- Conversa com o arquiteto para tirar dúvidas.

## Ferramentas
- GstarCAD 2022 LT (o 2024 está sem executável) controlado ao vivo por COM (`Gcad.Application`) via Python + pywin32. O usuário acompanha o desenho no 2º monitor.
- shapely: paredes calculadas como `pegada (cômodos com buffer de 15) − cômodos − vãos − janelas`. Paredes em comum saem uma vez só, sem linhas duplicadas.
- PyMuPDF para ampliar trechos do croqui (300 dpi); ffmpeg para folhas de contato dos vídeos (1 quadro/3 s, mosaico 4x4).

## Convenções adotadas
- Unidade cm; cotas do croqui = medidas **internas** (face a face); parede 15 cm.
- Referencial único da folha: x para a rua, y da divisa do fundo para o corredor lateral; no CAD X = −x, Y = y.
- Boneca padrão de 5 cm entre porta e parede perpendicular (exceções explícitas: 90 e 114).
- Camadas: ARQ-PAREDE, ARQ-PORTA, ARQ-JANELA, ARQ-COTA, ARQ-TEXTO, ARQ-LOUCA, ARQ-GRADE, ARQ-EXTERNO.
- Janela: `LxA/peitoril` (ex.: 150x120/100). Peitoril alto (≥150) indica banheiro.
- Sem projeção de telhado no levantamento (decisão do arquiteto).
- Itens estimados recebem nota "A CONFERIR" no desenho.

## Sequência que funcionou
1. Ler todas as folhas; identificar orientação de cada uma (números de cabeça para baixo = folha girada 180°).
2. Perguntar só o que muda o desenho: espessura de parede, cotas internas/externas, orientação, como as folhas se encaixam.
3. Desenhar folha por folha, começando pela mais completa; mostrar e corrigir antes de seguir.
4. Para cada folha: ampliar o croqui → listar cômodos e cotas → **somar as cadeias de cotas** → perguntar sobre o que não fecha → desenhar.
5. Quando o arquiteto edita direto no CAD: ler o DWG (dump COM), comparar com o modelo, incorporar nos scripts com medidas arredondadas e só então redesenhar.
6. Análise final automática: espessuras, sobreposição, varredura de portas, conectividade (unidades), limites do lote, áreas, cômodos sem janela.

## Decisões deste levantamento (resumo)
- Casa Frontal girada 180°; sala recuada 18 cm para a grade da sacada (1 m) ficar rente ao muro.
- Fundos 1 alinhada à Casa Frontal no lado do corredor (+16 cm distribuídos nos cômodos do corredor).
- Divergências resolvidas "confiando no lado do corredor": 485 → 414; 233 → 175; D/E alinhados na linha da bancada.
- Casa de cima colada no muro: corredor 155 → 162.
- 5 unidades no lote = 5 medidores vistos no vídeo (checagem cruzada útil).

## O que custou tempo (corrigir na skill)
- Croqui sem cadeia de cotas fechada: várias cotas só "batiam" com outras depois de perguntas.
- Folhas sem indicação de como se ligam; orientação deduzida pelos números invertidos e pelos vídeos.
- Larguras/aberturas sem cota: boneca, posição de porta, tanque, degrau.
- Fiz contas de comprimento disponível com erro uma vez (6,77 × 6,92) — a skill deve calcular, não estimar de cabeça.
- Redesenho apaga o desenho inteiro: obrigatório ler o DWG antes, se o usuário mexeu.
- Captura de tela fixa no monitor 2: depende da posição da janela.

Ver `CHECKLIST-LEVANTAMENTO.md` para o que conferir em campo.
