# Licenças e créditos

## Este projeto
Código, documentação e modelos: **MIT**, © 2026 Débora Diniz. Veja [LICENSE](../LICENSE). Você pode usar, copiar, modificar e redistribuir, mantendo o aviso de copyright e de licença.

## O que NÃO está no repositório (de propósito)
| Item | Por quê | Como obter |
|---|---|---|
| Efeitos sonoros do Mixkit | A licença permite uso em vídeos de YouTube, redes sociais e projetos comerciais, mas **proíbe redistribuir o som isoladamente, dentro de uma ferramenta ou template, ou com arquivos-fonte**. | `rodar.py sfx-baixar --sim` baixa direto do Mixkit para o seu computador. |
| Estalos de dedos (Wikimedia Commons, "Finger clicks", autor cori) | Domínio público; baixado junto, para manter o repositório leve. | `rodar.py sfx-baixar --sim` |
| Fontes Montserrat e Inter | SIL Open Font License 1.1 (livres). Baixadas do repositório google/fonts. | `rodar.py setup` |
| Modelo de transcrição (Whisper) | Licença MIT (OpenAI), baixado pela biblioteca faster-whisper. | Automático na primeira transcrição |
| ffmpeg | Binário estático baixado pelo pacote `static-ffmpeg`. O ffmpeg é LGPL/GPL conforme a compilação. | `rodar.py setup` |

## Efeitos sonoros sintéticos
Gerados por matemática no seu computador (`sfx_sinteticos.py`). Sem licença de terceiros.

## Dependências Python
numpy, scipy, OpenCV, Pillow, soundfile, faster-whisper, scenedetect, static-ffmpeg: cada uma com a sua licença de código aberto (BSD, MIT, Apache-2.0).

## O que você usa nos SEUS vídeos
- **Música, imagens e vídeos de terceiros:** use só o que for seu ou de licença que permita o uso (principalmente em anúncio pago). Guarde a origem em `assets/videos/CREDITOS.md`.
- **Sons de aplicativos de edição (CapCut e similares):** não extraia. A licença costuma valer só dentro do aplicativo.
- **Vídeos de referência de outros criadores:** servem para você estudar o ritmo e a estrutura. Não use o conteúdo, a marca, os textos nem os áudios deles.
- **Bancos de vídeo (Mixkit, Pexels, Pixabay):** leia a licença atual de cada um antes de usar em anúncio. As regras mudam.

## Aviso
Isto não é aconselhamento jurídico. Em caso de dúvida sobre uma licença, consulte o texto original da fonte ou um profissional.
