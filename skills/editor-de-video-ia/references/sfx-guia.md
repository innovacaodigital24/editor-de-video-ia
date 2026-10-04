# Efeitos sonoros

## De onde vêm
1. **Sintéticos (já vêm no `setup`):** gerados no seu computador, sem licença de terceiros. Nomes: `pop-sintetico`, `click-sintetico`, `snap-sintetico`, `whoosh-sintetico`, `whoosh-reverso-sintetico`, `impact-sintetico`, `riser-sintetico`, `bell-sintetico`.
2. **Biblioteca livre (opcional):** `rodar.py sfx-baixar --sim` baixa ~35 sons do Mixkit (licença livre para vídeos de YouTube, redes sociais e projetos comerciais; proibido redistribuir os sons em ferramentas ou templates; confira o texto atual da licença antes de usar em anúncio pago) e 4 estalos de dedos da Wikimedia (domínio público), e limpa tudo. **Os arquivos não fazem parte deste repositório**: cada pessoa baixa os seus.
3. **Os seus próprios arquivos:** coloque `.wav` em `assets/sfx/<categoria>/` e rode `rodar.py sfx-preparar --entrada assets/sfx --saida assets/sfx/pronto`.
- **Nunca extraia sons de aplicativos de edição** (CapCut e similares): a licença deles costuma valer só dentro do aplicativo.

## Categorias e nomes
`click`, `mouse-click`, `pop`, `pop-whoosh`, `bell`, `whoosh`, `impact`, `riser`, `snap`, `camera`, `success`, `typing`. Em `plano.json`, `"som"` aceita o nome do arquivo sem extensão (`pop__pop-seco-alerta`, `click-interface`), parte do nome, ou o caminho de um `.wav`. O motor procura em `assets/sfx/pronto/` do projeto, depois em `~/.config/editor-de-video-ia/sfx/pronto/`.

## Quando usar cada um
| Momento | Som | Pico sugerido |
|---|---|---|
| Primeiro quadro do vídeo | impacto grave suave | -18 dB |
| Punch-in (zoom rápido) | pop curto | -16 dB |
| Entrada de card | pop-whoosh | -13 dB |
| Item de lista aparecendo | click de interface | -19 dB |
| Frase mais forte | impact | -12 dB |
| Virada de assunto | whoosh ou estalo de dedos | -14 dB |
| Fim de uma lista de benefícios | bell suave | -21 dB |
| Corte em jump cut | pop bem baixo | -22 dB |

## Regras
- A voz manda. O efeito nunca compete com ela: nada acima de -12 dB de pico.
- Sincronize o início do som com o momento visual, não com o início do arquivo (sons limpos já não têm silêncio no começo).
- Não ligue som de clique a um botão que não existe na tela.
- Sons longos (impact, riser, typing) são cortados com fade pela limpeza. Se precisar de mais, use o `.wav` original.
- Medidas de uma biblioteca: use `sfx-preparar` para igualar o volume (RMS -22 dBFS, pico máx. -3 dBFS).
