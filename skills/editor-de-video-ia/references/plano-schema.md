# Formato do `plano.json`

O plano é o contrato entre a sua decisão de edição e o motor de renderização. **Todos os tempos são em segundos do vídeo ORIGINAL** (o motor converte para o vídeo depois dos cortes). Exemplo completo em `templates/plano.exemplo.json`. Valide sempre com `rodar.py validar`.

| Campo | Tipo | O que faz |
|---|---|---|
| `titulo` | texto | Nome base dos arquivos (`titulo_v1.mp4`). Sem espaços. |
| `formato` | `"9:16"`, `"16:9"`, `"1:1"`, `"4:5"` | Se omitido, segue a orientação do vídeo. Se diferente do gravado, reenquadra no centro. |
| `cortes` | `[[ini, fim], ...]` | Trechos que ficam. O que está entre eles sai. Use os `cortes_sugeridos` do `analisar` e ajuste. Pontos de corte em silêncio real, nunca no meio de palavra. |
| `legendas.ativa` | bool | Liga ou desliga. O estilo vem do `marca.json`. |
| `zoom.punches` | `[{"t": seg, "alvo": 1.12}]` | Zoom rápido (0,25s) nas palavras de peso. `alvo` opcional (1.09 a 1.15). Entre eles há zoom lento automático, e cada trecho após um corte muda de enquadramento. |
| `zoom.keyframes` | `[[t0,t1,z0,z1,"out"\|"io"]]` | Controle manual total (substitui o automático). |
| `cards` | lista | Cards no topo. Ver abaixo. Um por vez. |
| `inserts` | lista | Imagem ou vídeo em tela cheia por alguns segundos. Ver abaixo. |
| `sfx` | `[{"t": seg, "som": "nome", "pico_db": -16}]` | Efeito sonoro. `som` é o nome na biblioteca (`pop-whoosh-leve`, `click`, `pop-sintetico`...) ou caminho de um `.wav`. Som que não existe só gera aviso. |
| `audio` | `{lufs, highpass, compressor}` | Padrão: -16 LUFS, highpass 80 Hz, compressor leve. |
| `cor` | `natural`, `quente`, `frio`, `punchy`, `pb` | Color grade. |
| `vinheta` | bool | Escurece levemente as bordas (estilo cinematográfico). |
| `fade_out` | segundos | Fade no fim (padrão 0,3). |

## Cards
```json
{"tipo": "titulo", "t0": 6.4, "t1": 11.2, "rotulo": "PLANO DE AÇÃO",
 "titulo": [["IA ", true], ["NO SEU NEGÓCIO", false]], "sub": "onde entra hoje"}
```
O `true` marca a parte do título na cor de destaque.
```json
{"tipo": "lista", "t0": 11.8, "t1": 16.3, "rotulo": "VOCÊ GANHA",
 "itens": [["Menos retrabalho", 11.9], ["Processos rápidos", 13.1], ["Horas de volta", 14.4]]}
```
Cada item aparece no segundo indicado (use o momento em que a pessoa fala). Máximo 3 itens.
```json
{"tipo": "midia", "t0": 20, "t1": 24, "arquivo": "assets/imagens/print.png"}
```
Painel de imagem ou vídeo no topo. `zoom_minimo` (opcional) controla o espaço aberto para o card.

## Inserts (tela cheia)
```json
{"arquivo": "assets/videos/bastidor.mp4", "t0": 30, "t1": 33}
```
Entra com fade de 0,25s e tem zoom lento. A voz continua. Evite cards durante um insert.

## Regras que o `validar` confere
- Cortes em ordem, sem sobreposição. Cards sem sobreposição.
- Arquivos de mídia existem.
- Nenhum texto de card parece botão de CTA (se a marca pede isso).
- Nenhuma palavra de `vocabulario.evitar` nos textos de card.
- Avisa se há cards ou zooms demais para a duração.
