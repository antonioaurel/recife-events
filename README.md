# Eventos Recife

Agenda diária do Recife, Olinda e litoral: shows, frevo e prévias, feiras, teatro, o que fazer, onde comer (restaurantes e cafés) e onde beber.

Site: https://antonioaurel.github.io/recife-events/

## Como funciona

- `index.html` é a página inteira (HTML, CSS e JS num arquivo só).
- `data/*.json` são os dados, um arquivo por seção: `hoje`, `proximos`, `fazer`, `comer`, `beber`, `fechados`, `monitorados`. `data/meta.json` guarda a hora da última atualização.
- Uma tarefa agendada do Claude pesquisa a agenda toda manhã e faz commit só dos arquivos em `data/`.
- `og.png` é a imagem que aparece ao compartilhar o link (WhatsApp, Instagram, etc.).

## Cadastro de lugares

`data/lugares.json` é a lista de lugares (por enquanto, museus) que alimenta a aba Fontes, os museus em "Coisas para fazer" e os museus abertos do dia em "Hoje". Cada lugar tem os campos de texto originais (`hours`, `price`, `status`) e campos estruturados derivados deles:

- `situacao`: `aberto`, `verificar` ou `fechado` (lugares fechados ficam no cadastro mas não aparecem no site);
- `horarios`: faixas de horário por dia (`seg` a `dom`; lista vazia = fechado no dia);
- `gratis_dias`: dias com entrada grátis;
- `subcategory`, `confidence` (alta, media, baixa) e `verificado_em`.

`python3 tools/lugares.py validar` confere o cadastro; `python3 tools/lugares.py abertos AAAA-MM-DD` gera as linhas dos lugares abertos num dia.
