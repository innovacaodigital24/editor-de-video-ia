# Entrevista de marca

Objetivo: gerar o `marca.json` da pessoa para que todo vídeo saia com a identidade visual e as regras dela, e não com as de outra marca. Faça **uma única mensagem**, numerada, com opções sugeridas. A pessoa responde só com números ou com poucas palavras. O que ela não responder, assuma o padrão e avise.

## Antes de perguntar: tente descobrir sozinho
- Se a pessoa mandou um **logo, print do site ou do feed**, rode `rodar.py marca-cores imagem.png` e proponha as cores em hex.
- Se mandou um **link do site ou do Instagram**, use as ferramentas disponíveis (navegador) para olhar as cores, as fontes e o tom. Não afirme o que não viu.
- Se já existe `CLAUDE.md` ou manual de marca na pasta, leia e use.

## As perguntas (adapte a ordem ao que já souber)

**Sobre a marca**
1. Nome da marca ou do perfil (como aparece nos vídeos) e o que você vende ou ensina, em uma frase.
2. Quem assiste: (a) clientes finais (b) empresas (c) alunos e seguidores (d) outro.
3. Tom de voz: (a) direto e técnico (b) próximo e acolhedor (c) elegante e sofisticado (d) descontraído e divertido.

**Cores** (hex ou "escolhe você a partir do meu logo/site")
4. Cor de fundo dos cards (escura funciona melhor com texto claro).
5. Cor de destaque (palavra ativa da legenda, check dos cards, detalhes).
6. Cor secundária (rótulos e bordas dos cards).
7. Cor de apoio (opcional).
8. Cor do texto principal (padrão branco).

**Tipografia**
9. Fonte dos títulos e legendas: (a) Montserrat (b) Poppins (c) Inter (d) outra do Google Fonts: diga o nome. Se for outra, baixe com `rodar.py fonte "Nome"`.
10. Fonte do corpo: padrão Inter.

**Legendas**
11. Estilo: (a) karaokê palavra por palavra, a palavra ativa muda de cor (b) frase por frase (c) sem legenda.
12. Caixa alta nas legendas? (a) sim (b) não.

**Regras e vocabulário**
13. Palavras ou promessas que você NÃO quer que eu use nos textos que eu criar (cards, títulos). Exemplos: "grátis", "garantido", termos regulados do seu mercado.
14. Palavras que devem ganhar destaque na legenda (nomes de produtos, números, termos-chave).
15. Você vai usar os vídeos em **anúncios pagos**? (a) sim: não desenho botões de CTA na tela (a pessoa tenta clicar no vídeo; o botão real é o da plataforma) (b) não, só orgânico.
16. Tem regra de mercado que eu preciso respeitar (saúde, finanças, direito, educação)? Descreva.

**Padrões de edição**
17. Formato principal: (a) Reels, TikTok e Shorts 9:16 (b) YouTube 16:9 (c) os dois.
18. Ritmo padrão: (a) agressivo (b) dinâmico (c) calmo e cinematográfico.
19. Efeitos sonoros: (a) em cortes e zooms (b) só em impacto (c) nenhum. Trilha: (a) com música (b) sem música.
20. Logo ou marca d'água nos vídeos? (a) sim, mande o arquivo (b) não. E CTA final falado: qual frase você costuma usar?

## Depois das respostas
1. Monte `marca.json` a partir de `templates/marca.exemplo.json`. Preencha `nome`, `cores`, `fontes`, `legenda`, `palavras_destaque`, `vocabulario.evitar`, `regras`, `padroes`, `logo`. Guarde regras de mercado e tom em `notas`.
2. Rode `rodar.py validar --marca marca.json`. Ele confere os hex e avisa se o contraste texto/fundo é fraco.
3. Mostre um resumo curto: cores (com os hex), fontes, estilo de legenda, o que será evitado, regras ativas.
4. Peça confirmação. Ofereça: "Quer que eu salve isso como padrão para todos os seus vídeos?" Se sim, copie para `~/.config/editor-de-video-ia/marca.json`.
5. Ofereça um teste: renderizar 10 a 15 segundos de um vídeo dela para ela aprovar o visual antes de editar o primeiro vídeo inteiro.

## Cuidados
- Nunca invente cores nem fontes "da marca". Se não conseguiu ver, pergunte.
- Pergunta 13 e 15 são as que mais evitam retrabalho. Insista com gentileza.
- Dados pessoais e de clientes ficam fora do `marca.json`. Ele pode ser compartilhado com o time.
