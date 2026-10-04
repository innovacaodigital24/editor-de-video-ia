# Changelog

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/). Versionamento [SemVer](https://semver.org/lang/pt-BR/).

## [0.1.0] - 2026-10-03

Primeira versão pública.

### Adicionado
- Skill `editor-de-video-ia` com entrevista de marca, briefing, plano de edição com aprovação e entrega versionada (`prontos/tema_vN.mp4`).
- `analisar`: dados técnicos, transcrição com tempo por palavra (faster-whisper), silêncios, cenas e cortes sugeridos.
- `renderizar`: cortes, zoom automático com punch-ins, legendas karaokê, cards no topo (título, lista, mídia) que abrem espaço sem cobrir o rosto, imagens e vídeos em tela cheia, efeitos sonoros, áudio em -16 LUFS, cor, exportação H.264/AAC e legendas `.srt` e `.ass`.
- `validar`: confere `marca.json` e `plano.json`, incluindo regra de marca contra botão de CTA desenhado na tela, vocabulário a evitar e contraste de cores.
- Biblioteca de efeitos sonoros: sintéticos (sem licença) e download opcional de sons livres (Mixkit e Wikimedia) feito por cada usuário.
- `marca-cores` (cores a partir de uma imagem), `fonte` (Google Fonts), `teste` (teste de fumaça sem vídeo próprio).
- Documentação: passo a passo para iniciantes, como funciona, exemplos de pedidos, licenças e créditos.
