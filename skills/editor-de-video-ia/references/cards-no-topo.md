# Cards informativos no topo

Padrão de vídeos de alta retenção: a pessoa fica na metade de baixo da tela e, a cada 6 a 10 segundos, um card no topo resume o que ela acabou de dizer. Em um vídeo de ~45s, 3 a 4 cards.

## Tipos
- **titulo:** rótulo pequeno em caixa alta (cor secundária) + título de uma linha, com uma parte na cor de destaque + subtítulo opcional. Para apresentar um tema ou um próximo passo.
- **lista:** rótulo + até 3 itens que **aparecem um a um, no momento em que a pessoa fala cada um**, cada um com um check na cor de destaque. O card cresce conforme os itens entram.
- **midia:** painel de imagem ou vídeo no topo (print, gráfico, foto de produto).

## Como escolher o que vai em cada card
1. Releia a transcrição por trechos de 6 a 10s.
2. Escolha os momentos em que a pessoa **enumera** (lista), **nomeia** algo (título) ou **mostra** algo que se vê melhor (mídia).
3. Resuma com as palavras que ela usou. **Nunca invente** número, nome, resultado ou promessa. Respeite `vocabulario.evitar` do `marca.json` (o `validar` confere).
4. Sincronize cada item com a palavra falada (tempo do Whisper, ajustado ao início real da fala).
5. Nunca desenhe botão ou texto que pareça clicável (regra de marca).

## O que o motor faz sozinho
- Entrada: desliza 40px de cima com fade em 0,45s (ease-out); saída em 0,3s.
- **Abre espaço no enquadramento:** enquanto o card aparece, o vídeo dá um zoom suave e desce, de modo que o card nunca cubra o rosto. O motor estima o topo da cabeça com detecção de rosto (se não achar, usa 24% da altura).
- Posição: ~10% da altura (zona segura), largura ~89% em 9:16. Em 16:9 o card vai no canto superior esquerdo com 40% da largura.
- Cores, fontes e bordas vêm do `marca.json`. O texto longo encolhe sozinho para caber.

## Boas práticas
- Um card por vez, nunca sobrepostos. Deixe pelo menos 1s entre cards.
- Duração mínima de 2,5s para dar tempo de ler; títulos curtos (até ~22 caracteres).
- Não use card durante uma imagem ou vídeo em tela cheia.
- Efeito sonoro de entrada (pop-whoosh) e click nos itens da lista funcionam bem, com volume baixo.
