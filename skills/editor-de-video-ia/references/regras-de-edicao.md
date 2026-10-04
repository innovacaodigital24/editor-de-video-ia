# Regras de edição (o que torna o vídeo profissional)

Números testados em vídeos 9:16 de talking head de ~45s. Ajuste ao ritmo escolhido, mas não abra mão dos princípios.

## Cortes
- Silêncios: remova o que passa de ~0,4s, deixando 0,08s (agressivo) ou 0,2s (suave) nas pontas. O corte cai em **silêncio real** (verifique a energia do áudio, não só o tempo do Whisper, que costuma marcar a primeira palavra depois de uma pausa até 0,25s cedo).
- Nunca corte no meio de uma palavra.
- Alinhe os cortes a fronteiras de quadro (30 fps).
- Corte que mostra "pulo" na imagem de câmera parada: mude o enquadramento depois do corte (o zoom automático já faz isso).

## Gancho
- Os 3 primeiros segundos decidem. Se o vídeo não começa forte, sugira reordenar ou começar pela frase mais forte. Pergunta direta ou promessa concreta logo no primeiro quadro.
- Sem intro, sem fade de entrada no vídeo (o fade de saída de 0,3s é ok).

## Movimento
- **Punch-in:** 1.0 para ~1.06 a 1.15 em 0,25s, ease-out cúbico (nunca linear), nas palavras de peso. Nunca dois iguais seguidos.
- **Zoom lento (Ken Burns):** 1.0 para ~1.07 ao longo do plano.
- Um punch a cada 2 a 4 cortes ou frases. Em ritmo calmo, menos.
- Glitch e RGB split: só em tensão ou revelação, máximo 3 por vídeo. Flash cut de 2 frames só em virada de assunto.
- Transições nunca passam de 0,4s em ritmo rápido.

## Legendas
- Karaokê: máx. 4 palavras por tela. Outros estilos: máx. 2 linhas.
- Fonte extrabold, contorno preto de 6px e sombra suave (legível em tela pequena e fundo claro).
- 9:16: ~78% da altura, centralizada, acima da interface do app. Nada a menos de 10% das bordas.
- Palavra ativa na cor de destaque com escala 1.12 por 3 quadros; palavras de peso (números, termos da marca) escalam 1.2.
- A legenda é a fala. Não reescreva.
- Confira nomes próprios e termos técnicos na transcrição antes de renderizar.

## Áudio
- Voz: highpass 80 Hz, compressor suave (3:1, limiar -18 dB), normalização em **-16 LUFS** com pico abaixo de -1,5 dBTP.
- Música: -22 dB com ducking de -8 dB quando há fala. Efeitos: pico em ~-12 a -19 dB (nunca competem com a voz). Fade de 0,05s no início e 0,3s no fim.
- Sem música quando a pessoa pedir: só voz e efeitos.

## Efeitos sonoros (resumo; detalhes em `sfx-guia.md`)
- Pop nos zooms, pop-whoosh na entrada de card, click em cada item de lista, impacto grave na frase mais forte, estalo de dedos numa virada de assunto, bell suave no fim de uma lista.
- Menos é mais: som em tudo cansa. Se o efeito não serve à narrativa, ele sai.

## Cor
- Natural: contraste +4%. Quente e frio deslocam vermelho e azul levemente. Punchy: contraste +8% e saturação +10%. Vinheta leve só em estilo cinematográfico.

## Exportação
- H.264, CRF 18, preset slow, yuv420p, AAC 320 kbps 48 kHz estéreo, `-movflags +faststart`, quadros por segundo estáveis (30).
- Resoluções: 1080x1920 (9:16), 1920x1080 (16:9), 1080x1080 (1:1), 1080x1350 (4:5).

## Verificação antes de entregar
1. `ffprobe`: resolução, duração, áudio presente.
2. Loudness: ~-16 LUFS, pico abaixo de -1 dBFS.
3. Olhar 6 a 8 quadros: cards sem cobrir o rosto, legendas inteiras na tela, nada na zona de interface do app.
4. Dizer o que NÃO foi verificado (o assistente não ouve o áudio nem assiste ao vídeo em movimento).
