# Eventos Recife

Agenda diária do Recife, Olinda e litoral: shows, frevo e prévias, feiras, teatro, o que fazer, onde comer (restaurantes e cafés) e onde beber.

Site: https://antonioaurel.github.io/recife-events/

## Como funciona

- `index.html` é a página inteira (HTML, CSS e JS num arquivo só).
- `data/*.json` são os dados, um arquivo por seção: `hoje`, `proximos`, `fazer`, `comer`, `beber`, `fechados`, `monitorados`. `data/meta.json` guarda a hora da última atualização.
- Uma tarefa agendada do Claude pesquisa a agenda toda manhã e faz commit só dos arquivos em `data/`.
- `og.png` é a imagem que aparece ao compartilhar o link (WhatsApp, Instagram, etc.).
