# Como contribuir

Obrigada por querer ajudar. Contribuições são bem-vindas: correções, melhorias de documentação, novos estilos de card, novos formatos, testes em outros sistemas (principalmente Windows e Linux).

## Antes de abrir um pull request
1. Abra uma **issue** descrevendo o problema ou a ideia (use os modelos prontos).
2. Faça um fork e crie um branch com um nome claro (`corrige-legenda-16x9`).
3. Rode os testes:
   ```bash
   python3 -m unittest discover tests          # testes rápidos, sem dependências
   python3 install.py --sem-copia              # prepara o ambiente
   python3 skills/editor-de-video-ia/scripts/rodar.py teste
   ```
4. Descreva no PR o que mudou e o que você testou (sistema, versão do Python).

## Regras do projeto
- **Nada de arquivos de terceiros** no repositório (músicas, sons, imagens, vídeos, fontes). Se precisar de um recurso, adicione um script que baixe da fonte e a licença em `docs/LICENCAS-E-CREDITOS.md`.
- **Nada de dados pessoais**: vídeos, transcrições, telefones, chaves de API ou `marca.json` de alguém.
- Mensagens e documentação em **português do Brasil**, claras para quem não é de tecnologia.
- Regras de marca (CTA, vocabulário, contraste) devem ser **verificadas pelo `validar.py`**, não só descritas.
- Mantenha o motor **determinístico**: o mesmo plano gera o mesmo vídeo.

## Estilo de código
Python 3.9+, bibliotecas já listadas em `requirements.txt`, funções curtas e comentários só onde o motivo não é óbvio.
