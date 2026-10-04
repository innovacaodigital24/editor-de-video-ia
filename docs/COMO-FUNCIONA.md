# Como funciona

## Visão geral

O Claude Code é o "editor": ele conversa com você, decide a edição e escreve um **plano** em JSON. Os scripts Python fazem o trabalho pesado (análise e render). Cada parte tem uma responsabilidade:

| Parte | O que faz |
|---|---|
| `SKILL.md` + `references/` | O roteiro e o conhecimento de edição que o assistente segue |
| `marca.json` | Sua identidade: cores, fontes, legenda, vocabulário, regras |
| `scripts/analisar.py` | ffprobe, transcrição (faster-whisper), silêncios, cenas, cortes sugeridos |
| `plano.json` | A decisão de edição: cortes, zooms, cards, mídias, sons, cor |
| `scripts/validar.py` | Confere `marca.json` e `plano.json` antes de gastar tempo renderizando |
| `scripts/renderizar.py` | Aplica o plano quadro a quadro e mixa o áudio |

## O que o motor faz em cada quadro

1. Lê o quadro do vídeo original (ffmpeg), já no formato de saída.
2. Pula os quadros dos trechos cortados.
3. Aplica zoom (lento + punch-ins) e, quando há card, abre espaço para ele sem cobrir o rosto.
4. Aplica a cor (grade) e a vinheta.
5. Mistura imagens ou vídeos em tela cheia (se houver).
6. Desenha o card do topo e a legenda karaokê.
7. Envia o quadro para o x264 (CRF 18).

Em paralelo, o áudio original é cortado nos mesmos trechos, tratado (highpass, compressor, loudnorm -16 LUFS), recebe os efeitos nos tempos do plano e é muxado com o vídeo.

## Decisões de projeto

- **Local primeiro:** nada vai para a nuvem. A transcrição usa o modelo Whisper no seu computador.
- **Plano antes do render:** você vê e aprova o que será feito. O plano é um arquivo, então é reproduzível e ajustável (v2, v3).
- **Regras viram código:** o que é regra da marca (sem botão de CTA, vocabulário a evitar, contraste) é verificado pelo `validar`, não só "lembrado" pelo assistente.
- **Licença é requisito:** nenhum arquivo de terceiros é distribuído; sons livres são baixados por quem usa; sintéticos são gerados localmente.
- **Cortes em silêncio real:** os cortes usam a energia do áudio, porque o Whisper marca o começo das frases com atraso ou adiantamento de até ~0,25s depois de pausas.
- **Nunca sobrescrever:** o original é copiado para o projeto e as entregas são numeradas.

## Fontes de dados

- Tempos de palavra: faster-whisper (modelo `small` por padrão), com correção do início da primeira palavra de cada frase.
- Silêncios: ffmpeg `silencedetect` (-35 dB, 0,4s).
- Cenas: PySceneDetect.
- Rosto (para posicionar os cards): classificador Haar do OpenCV, em 8 quadros do vídeo.

## Limites conhecidos

- Cards de cima assumem uma pessoa centralizada no quadro. Com duas pessoas ou enquadramento muito diferente, ajuste `zoom_minimo` ou use só cards de título.
- Em 16:9, os cards ficam no canto superior esquerdo e não deslocam o enquadramento.
- Vídeos HDR (HLG) do iPhone podem ficar desbotados; prefira gravar em SDR.
