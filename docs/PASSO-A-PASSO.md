# Passo a passo para iniciantes

Este guia é para quem nunca usou o terminal. Leva uns 15 minutos na primeira vez.

## 1. O que você precisa ter

1. **Claude Code ou Codex instalado no computador** (app de desktop ou terminal) e com login feito. A skill não funciona no ChatGPT nem no Claude pelo navegador, porque edita o vídeo na sua máquina.
   - **Claude Code:** baixe em [claude.com/claude-code](https://claude.com/claude-code). Precisa de **plano pago do Claude** (Pro ou superior).
   - **Codex:** baixe em [openai.com/codex](https://openai.com/codex). Precisa de **plano pago do ChatGPT** (Plus ou superior).
2. **Python 3.9 ou mais novo.**
   - Mac: abra o app **Terminal** e digite `python3 --version`. Se aparecer algo como `Python 3.9.6` ou maior, está ok. Se pedir para instalar as ferramentas de desenvolvedor, aceite.
   - Linux: `python3 --version` (instale pelo gerenciador do seu sistema se faltar).
3. **Git** (opcional). Se não tiver, você baixa o ZIP (passo 2, opção B).

## 2. Baixar o repositório

**Opção A, com git:** no Terminal:

```bash
git clone https://github.com/innovacaodigital24/editor-de-video-ia.git
cd editor-de-video-ia
```

**Opção B, sem git:** na página do repositório no GitHub, clique no botão verde **Code** e depois em **Download ZIP**. Descompacte e, no Terminal, entre na pasta (digite `cd ` com um espaço e arraste a pasta para dentro da janela do Terminal, depois Enter).

## 3. Instalar

```bash
python3 install.py
```

Ele coloca a skill no lugar certo para o Claude Code e para o Codex e instala tudo o que precisa (uns 2 minutos, com internet). No fim aparece "Pronto".

Para conferir:

```bash
python3 ~/.claude/skills/editor-de-video-ia/scripts/rodar.py teste
```

Se aparecer **TESTE OK**, está tudo certo.

## 4. Crie a pasta do seu projeto de vídeo

Crie uma pasta, por exemplo `Meus Videos`, em qualquer lugar. Dentro dela o assistente vai criar sozinho: `assets/` (seu material), `saida/` (arquivos de trabalho) e `prontos/` (vídeos finais).

Abra o **Claude Code ou o Codex nessa pasta** (no app de desktop, escolha a pasta ao iniciar uma conversa). Se o Codex já estava aberto durante a instalação, feche e abra de novo.

## 5. Peça a edição

Escreva:

> Edita esse vídeo

e anexe o arquivo de vídeo (ou diga o caminho dele).

### Primeira vez: a entrevista de marca
O assistente vai mandar uma mensagem com perguntas numeradas: nome da marca, cores, fontes, estilo de legenda, palavras a evitar, regras de anúncio... Responda só com os números e poucas palavras. Dicas:
- **Não sabe os códigos das cores?** Mande o logo, um print do seu site ou do seu feed e peça "sugira as cores".
- **Não sabe a fonte?** Diga "escolhe você" ou cite uma do Google Fonts.
- Ele mostra um resumo e pede sua confirmação. Responda "pode salvar como padrão" para não repetir.

### Depois: análise, plano e render
1. Ele analisa o vídeo (formato, duração, silêncios, transcrição) e faz poucas perguntas.
2. Mostra o **plano de edição** em uma tabela. Se estiver bom, diga **"pode render"**. Se quiser mudar, diga o quê.
3. Ele renderiza e entrega em `prontos/`.

## 6. Assista antes de postar

Sempre assista ao vídeo inteiro com som. O assistente confere medidas e olha alguns quadros, mas não ouve o áudio. Confira nomes e termos técnicos nas legendas.

## 7. Ajustes

Diga o que quer mudar ("tira o terceiro card", "legenda um pouco maior", "mais calmo"). Ele gera a **v2** e mantém a v1.

## 8. Nos próximos vídeos

Diga: **"Edita esse vídeo, mesmo estilo do último, confia, manda ver."** Ele usa seu padrão salvo, pula as perguntas e a aprovação do plano.

## Dúvidas comuns

| Pergunta | Resposta |
|---|---|
| Meu vídeo sai da minha máquina? | O arquivo não vai para nenhum serviço de edição: edição, transcrição e render rodam no seu computador. Mas o assistente (Claude ou Codex) lê a transcrição e olha alguns quadros para conferir o resultado, então esse conteúdo passa pela IA. Não use vídeos com dados de terceiros sem autorização. |
| Posso usar minhas imagens e vídeos? | Sim. Coloque em `assets/imagens` e `assets/videos` e diga onde entram. |
| Posso colocar música? | Sim, envie o arquivo (precisa ser sua ou de licença livre). O assistente também pode gerar o vídeo sem música. |
| Deu erro. E agora? | Veja [a tabela de problemas](../skills/editor-de-video-ia/references/solucao-de-problemas.md) ou peça ao próprio assistente: "o que deu errado?". |
| Como atualizo a skill? | `git pull` na pasta do repositório e `python3 install.py` de novo. |
| Funciona no ChatGPT ou no Claude do navegador? | Não. Precisa do Claude Code ou do Codex instalado no computador, com plano pago. |
| Como desinstalo? | Apague `~/.claude/skills/editor-de-video-ia`, `~/.agents/skills/editor-de-video-ia` e `~/.config/editor-de-video-ia`. |
