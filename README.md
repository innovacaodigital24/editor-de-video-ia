# Editor de Vídeo IA

**Uma skill para Claude Code e Codex que edita seus vídeos curtos de ponta a ponta, com a identidade visual da SUA marca.**

Você grava, entrega o vídeo bruto e recebe de volta o MP4 pronto para postar: cortes de silêncio, legendas karaokê palavra por palavra, cards informativos no topo, zooms, efeitos sonoros, áudio tratado e cor. Na primeira vez, o assistente faz uma **entrevista de marca** para aprender suas cores, fontes, tom e regras, e depois todo vídeo sai no seu padrão.

Criada por **Débora Diniz** ([@eusoudeboradiniz](https://instagram.com/eusoudeboradiniz)) · Licença MIT

---

## O que você ganha

- **Entrevista de marca** na primeira vez: cores, fontes, estilo de legenda, palavras a evitar e regras do seu mercado ficam salvas em um `marca.json`.
- **Análise automática** do vídeo: formato (Reels ou YouTube), transcrição com tempo por palavra, mapa de silêncios, cenas e sugestão de cortes.
- **Plano de edição antes do render:** você vê e aprova o que será feito.
- **Legendas karaokê** na cor da sua marca, com destaque para as palavras de peso.
- **Cards no topo** (título e lista) que resumem o que você fala, no momento em que você fala. O enquadramento abre espaço sozinho para o card nunca cobrir seu rosto.
- **Zooms e movimento** com ritmo calmo, dinâmico ou agressivo, sem repetir o mesmo enquadramento.
- **Imagens, vídeos e B-roll** seus (ou sugeridos por assunto, com a sua aprovação).
- **Efeitos sonoros** (pop, click, whoosh, impacto, bell, estalo) e áudio normalizado em -16 LUFS.
- **Validação de regras da sua marca:** por exemplo, nenhum botão de CTA desenhado na tela em anúncios, e nenhuma palavra da sua lista de "evitar" nos textos criados pelo assistente.
- **Entrega organizada:** `prontos/tema_v1.mp4`, `tema_v2.mp4`... (nunca sobrescreve), com as legendas `.srt` e `.ass`.

## Como funciona

```
 vídeo bruto ─► analisar ─► plano de edição ─► você aprova ─► renderizar ─► prontos/tema_v1.mp4
                  │              ▲                                │
   transcrição, silêncios,       │                          legenda .srt e .ass
   cenas, cortes sugeridos   marca.json (suas cores, fontes e regras)
```

A edição roda **no seu computador**: o ffmpeg, a transcrição (Whisper) e o render. Nenhum serviço de edição na nuvem recebe o seu vídeo. **Atenção:** o assistente (Claude ou Codex) lê a transcrição e olha alguns quadros do vídeo para conferir o resultado, então esse conteúdo passa pela IA. Não use vídeos com dados de clientes, pacientes ou terceiros sem autorização.

## Requisitos

> **Leia antes de instalar.** Esta skill edita o vídeo **no seu computador**, então precisa de um assistente de IA que rode programas na sua máquina. O ChatGPT e o Claude no navegador ou no app de conversa **não fazem isso**.

- **Um destes dois, instalado no computador** (app de desktop ou terminal):
  - [Claude Code](https://claude.com/claude-code), da Anthropic. Precisa de **plano pago do Claude** (Pro ou superior).
  - [Codex](https://openai.com/codex), da OpenAI. Precisa de **plano pago do ChatGPT** (Plus ou superior).
- **Python 3.9 ou mais novo.**
- Uns 2 GB livres (bibliotecas e modelo de transcrição) e internet na primeira instalação.
- macOS ou Linux. Windows: ainda não testado (veja [Limitações](#limitações-honestas)).

Não precisa instalar o ffmpeg: a instalação baixa um binário próprio, isolado.

## Instalação

```bash
git clone https://github.com/innovacaodigital24/editor-de-video-ia.git
cd editor-de-video-ia
python3 install.py
```

O `install.py` instala a skill para os dois assistentes (`~/.claude/skills/editor-de-video-ia` para o Claude Code e `~/.agents/skills/editor-de-video-ia` para o Codex) e prepara o ambiente (uns 2 minutos). Quer só um? `python3 install.py --para claude` ou `python3 install.py --para codex`. Se o Codex já estava aberto, feche e abra de novo.

**Jeito mais fácil:** abra o Claude Code ou o Codex e cole: *"Instala para mim a skill Editor de Vídeo IA deste repositório: https://github.com/innovacaodigital24/editor-de-video-ia. Siga as instruções do README (clonar, rodar o install.py e depois o teste) e me avise quando estiver pronta."*

> **Passo a passo para quem nunca usou terminal:** [docs/PASSO-A-PASSO.md](docs/PASSO-A-PASSO.md)

**Opção B, como plugin, só no Claude Code** (se a sua versão do Claude Code tiver suporte a plugins): `/plugin marketplace add innovacaodigital24/editor-de-video-ia` e depois `/plugin install editor-de-video-ia`. Depois, rode o ambiente uma vez: `python3 ~/.claude/plugins/.../scripts/rodar.py setup` (a skill avisa o caminho exato).

**Conferir se está tudo certo** (não usa nenhum vídeo seu, leva ~1 minuto):

```bash
python3 ~/.claude/skills/editor-de-video-ia/scripts/rodar.py teste
```

## Seu primeiro vídeo

1. Crie uma pasta para o projeto e abra o Claude Code ou o Codex nela.
2. Diga: **"Edita esse vídeo"** e anexe o arquivo (ou diga onde ele está).
3. **Na primeira vez**, o assistente faz a entrevista de marca (20 perguntas numeradas, você responde com números). Pode mandar seu logo, o link do site ou um print do feed para ele sugerir as cores.
4. Ele analisa o vídeo, faz poucas perguntas e mostra o **plano de edição**.
5. Você diz **"pode render"** (ou pede ajustes).
6. O vídeo pronto aparece em `prontos/`. Quer mudar algo? Diga o que, e ele gera a v2 sem apagar a v1.

Nos próximos vídeos: **"mesmo estilo do último, confia, manda ver"** e ele pula as perguntas.

Mais frases prontas: [docs/EXEMPLOS-DE-PEDIDOS.md](docs/EXEMPLOS-DE-PEDIDOS.md).

## Imagens, vídeos e sons seus

Coloque na pasta do projeto: `assets/imagens/`, `assets/videos/`, `assets/sfx/`. Diga o arquivo, o momento e o jeito ("aos 12s entra o print `resultado.png` em tela cheia por 3s"). Se você não indicar nada, o assistente propõe no plano onde cada material pode entrar, e sugere B-roll de bancos livres só com a sua aprovação.

Para ter uma biblioteca de sons (pop, click, whoosh, impacto, bell, estalo): `python3 ~/.claude/skills/editor-de-video-ia/scripts/rodar.py sfx-baixar --sim`. Os arquivos **não vêm neste repositório** (a licença do Mixkit proíbe redistribuir os sons dentro de uma ferramenta ou template); cada pessoa baixa os seus. Sem isso, funcionam os efeitos sintéticos que já vêm na instalação.

## Estrutura do repositório

```
editor-de-video-ia/
├── install.py                      instala a skill e o ambiente
├── skills/editor-de-video-ia/
│   ├── SKILL.md                    o roteiro que o assistente segue
│   ├── references/                 entrevista de marca, briefing, regras de edição, cards, sons, mídias...
│   ├── scripts/                    analisar, renderizar, validar, sons, fontes, testes
│   └── templates/                  marca.exemplo.json, plano.exemplo.json, catálogo de sons
├── docs/                           passo a passo, como funciona, exemplos, licenças
├── examples/                       perfis de marca de exemplo
├── tests/                          teste automático
└── .github/                        CI e modelos de issue
```

## Personalização

Tudo que é "da sua marca" fica no `marca.json` (cores, fontes, legenda, palavras de destaque, vocabulário a evitar, regras). O assistente gera na entrevista, mas você pode editar à mão. Veja [examples/](examples/) e [skills/editor-de-video-ia/templates/marca.exemplo.json](skills/editor-de-video-ia/templates/marca.exemplo.json).

## Limitações honestas

- O assistente **não ouve o áudio nem assiste ao vídeo em movimento**: ele confere medidas (volume, duração, resolução) e olha quadros. Sempre assista ao resultado antes de postar.
- Testado em vídeos **talking head** verticais (9:16) de até 2 minutos, no macOS. O formato 16:9 e os cards em vídeo horizontal funcionam, mas têm menos testes. Windows ainda não foi testado.
- A transcrição (Whisper) erra nomes próprios e termos técnicos: revise nomes de marcas e produtos antes de renderizar.
- Os cards usam detecção de rosto simples; se não achar o rosto, assume uma posição padrão.
- É uma ferramenta de edição de propósito específico (vídeo curto de uma pessoa falando), não um editor de linha do tempo como o Premiere ou o CapCut.

## Licenças e créditos

Código sob [MIT](LICENSE). Fontes Montserrat e Inter (SIL OFL) são baixadas na instalação. Os efeitos sonoros sintéticos são gerados no seu computador. Detalhes e regras de uso de músicas, sons e imagens de terceiros: [docs/LICENCAS-E-CREDITOS.md](docs/LICENCAS-E-CREDITOS.md).

## Contribuir

Veja [CONTRIBUTING.md](CONTRIBUTING.md). Achou um problema? Abra uma issue com o modelo pronto.

## Autora

**Débora Diniz** — especialista em IA e empreendedora, mais de 22 anos em tecnologia. Esta skill nasceu da rotina real de produção de vídeos dela e é compartilhada com seus alunos e com a comunidade.

Instagram: [@eusoudeboradiniz](https://instagram.com/eusoudeboradiniz)
