# Imagens, vídeos e B-roll

## Material do próprio usuário (sempre a primeira escolha)
Pasta do projeto: `assets/imagens/` e `assets/videos/`. O usuário diz **arquivo, momento e jeito**:
- "Aos 12s entra `resultado.png` em tela cheia por 3s" → `inserts`.
- "Em 'plano de ação', mostra `dashboard.mp4` no painel do topo" → card `midia`.
- "Usa o que está na pasta assets" → você propõe no plano onde cada material entra, de acordo com a fala.

No plano, liste cada inserção: tempo, arquivo, posição, animação. Imagens ganham zoom lento; vídeos tocam no tempo normal (e repetem se forem curtos).

## Quando faltar material (B-roll)
Proponha B-roll **no plano de edição**, com o termo de busca e o link de cada clipe. **Baixe só o que o usuário aprovar.** Dosagem: no máximo 1 inserção a cada 6 a 8s num talking head, de 2 a 4s, só quando ilustra o que está sendo dito.

Fontes, em ordem:
1. **Mixkit (vídeos gratuitos):** sem conta. Use só clipes da "Stock Video Free License"; evite os "Restricted". Poucas requisições, sem coleta em massa.
2. **Pixabay** via API oficial (chave gratuita que a pessoa cria e guarda em `~/.config/pixabay/api_key`; nunca peça a chave no chat).
3. **Pexels:** pelo site, com a pessoa logada, em baixo volume, ou download manual dela. A API do Pexels pode estar com emissão de chaves pausada.
- Termos de busca em inglês, orientação vertical para 9:16, resolução de pelo menos 1080p.
- Evite pessoas reconhecíveis de forma que sugira endosso, marcas visíveis e conteúdo sensível.
- Registre em `assets/videos/CREDITOS.md`: link, autor, data.

## Imagens geradas
- **Gráficos por código** (cards, infográficos, números em destaque, mockups, fundos animados) na identidade da marca: sempre possível e consistente.
- **Ilustrações com IA** só por ferramentas que o usuário tenha disponíveis e com a confirmação dele. Diga que é imagem gerada.

## Fundos animados
Crie por código nas cores da marca (gradientes em movimento, grade de dados, partículas) em loop de 6s. Evite baixar fundos de sites de templates pagos: a licença costuma valer só para sites, não para vídeo.

## Licenças, sempre
Pergunte de onde veio qualquer material do usuário que pareça de terceiros (print de outro perfil, música, clipe). Se não for dele nem de licença livre, avise do risco antes de usar em anúncio.
