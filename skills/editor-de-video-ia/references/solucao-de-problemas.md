# Solução de problemas

| Sintoma | Causa provável | O que fazer |
|---|---|---|
| `Ambiente ainda não instalado` | `setup` não foi rodado | `python3 scripts/rodar.py setup` |
| `ffmpeg não encontrado` | download do binário falhou | Rode `setup` de novo com internet. Alternativa: instale o ffmpeg do sistema (`brew install ffmpeg` no Mac, `sudo apt install ffmpeg` no Linux, `winget install ffmpeg` no Windows). |
| Falha ao baixar fontes | sem internet ou GitHub bloqueado | `rodar.py setup --sem-fontes` e coloque `Montserrat.ttf` e `Inter.ttf` em `~/.config/editor-de-video-ia/fonts/`. |
| Transcrição lenta | modelo grande | Use `--modelo base` (menos preciso) ou `tiny`. A primeira execução baixa o modelo, uma vez só. |
| Nomes próprios errados na legenda | limite do Whisper | Corrija em `saida/analise/transcricao.json` antes de renderizar. |
| `Plano inválido` | `validar` achou um problema | Leia a mensagem: ela diz o campo e o motivo. |
| Card "parece um botão de CTA" | regra de marca ativa | Tire o texto do card; o CTA fica na fala. Para desativar: `regras.sem_botao_cta_na_tela = false` em `marca.json` (não recomendado em anúncios). |
| Card cobrindo o rosto | rosto não detectado ou pessoa muito alta no quadro | Aumente `zoom_minimo` do card (1.12 a 1.16) ou use cards só do tipo `titulo`. |
| Legenda sai da tela | palavra muito longa | O motor encolhe a fonte; se ainda falhar, reduza `legenda.tamanho` em `marca.json`. |
| `som não encontrado` | nome do efeito não existe | Veja `ls ~/.config/editor-de-video-ia/sfx/pronto/` e ajuste o `som` no plano. O render continua sem esse som. |
| Vídeo final sem áudio | original sem faixa de áudio | Confira com `ffprobe`. O motor gera só os efeitos. |
| Vídeo do iPhone em HDR parece desbotado | HDR HLG | Grave em SDR (Ajustes > Câmera > Formatos > desative HDR) ou peça `cor: "punchy"`. |
| Render muito lento | preset slow em vídeo longo | Use `--preview` para conferir; renderize em partes se o vídeo passar de 5 minutos. |
| `Falha ao gravar o vídeo` | disco cheio ou ffmpeg encerrou | Veja o espaço em disco e as mensagens do ffmpeg acima. |

Para testar se tudo está certo, sem usar um vídeo seu: `python3 scripts/rodar.py teste`.

Windows: use `py` no lugar de `python3` e prefira rodar pelo WSL ou pelo Git Bash. O motor foi testado em macOS; o teste automático do repositório roda em Linux; Windows não foi testado.
