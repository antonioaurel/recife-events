#!/usr/bin/env python3
"""Cadastro de lugares (data/lugares.json) do site Eventos Recife.

Uso:
  python3 tools/lugares.py validar
      Confere o formato do cadastro e lista problemas.
  python3 tools/lugares.py abertos AAAA-MM-DD [--pular id1,id2]
      Imprime (JSON) as linhas de hoje.json dos lugares abertos nessa data,
      com horário do dia e preço do dia (dias grátis). Lugares com
      situacao "fechado" e os "verificar" de confiança baixa ficam de fora.
"""
import datetime
import json
import re
import sys
from pathlib import Path

ARQ = Path(__file__).resolve().parent.parent / 'data' / 'lugares.json'
DIAS = ['seg', 'ter', 'qua', 'qui', 'sex', 'sab', 'dom']
NOMES = {'seg': 'segunda', 'ter': 'terça', 'qua': 'quarta', 'qui': 'quinta', 'sex': 'sexta', 'sab': 'sábado', 'dom': 'domingo'}
SITUACOES = {'aberto', 'verificar', 'fechado'}
CONFIANCAS = {'alta', 'media', 'baixa'}
OBRIGATORIOS = ['id', 'category', 'name', 'city', 'neighborhood', 'address', 'hours',
                'horarios', 'price', 'gratis_dias', 'status', 'situacao', 'confidence']
HORA = re.compile(r'^\d{2}:\d{2}$')


def carregar():
    return json.loads(ARQ.read_text(encoding='utf-8'))


def validar(dados):
    erros = []
    vistos = set()
    for i, p in enumerate(dados.get('places', [])):
        nome = p.get('id', f'#{i}')
        for campo in OBRIGATORIOS:
            if campo not in p:
                erros.append(f'{nome}: falta o campo {campo}')
        if nome in vistos:
            erros.append(f'{nome}: id repetido')
        vistos.add(nome)
        if not re.match(r'^[a-z0-9-]+$', str(p.get('id', ''))):
            erros.append(f'{nome}: id deve ser kebab-case')
        if p.get('situacao') not in SITUACOES:
            erros.append(f'{nome}: situacao inválida ({p.get("situacao")})')
        if p.get('confidence') not in CONFIANCAS:
            erros.append(f'{nome}: confidence inválida ({p.get("confidence")})')
        for campo in ('website', 'instagram'):
            u = p.get(campo)
            if u and not str(u).startswith(('http://', 'https://')):
                erros.append(f'{nome}: {campo} não é URL')
        h = p.get('horarios', {})
        if set(h) != set(DIAS):
            erros.append(f'{nome}: horarios precisa ter as chaves {",".join(DIAS)}')
        for d, faixas in h.items():
            for f in faixas:
                if len(f) != 2 or not all(HORA.match(x) for x in f) or f[0] >= f[1]:
                    erros.append(f'{nome}: faixa inválida em {d}: {f}')
        for d in p.get('gratis_dias', []):
            if d not in DIAS:
                erros.append(f'{nome}: gratis_dias com dia inválido ({d})')
        if p.get('situacao') == 'aberto' and not any(h.values()):
            erros.append(f'{nome}: aberto mas sem nenhum horário')
    return erros


def abertos(dados, data, pular=()):
    d = DIAS[datetime.date.fromisoformat(data).weekday()]
    linhas = []
    for p in dados['places']:
        if p['id'] in pular or p['situacao'] == 'fechado':
            continue
        if p['situacao'] == 'verificar' and p['confidence'] == 'baixa':
            continue
        faixas = p['horarios'].get(d) or []
        if not faixas:
            continue
        horario = ', '.join(f'{a} a {b}' for a, b in faixas)
        gratis = d in p.get('gratis_dias', [])
        preco = ('Grátis' if len(p.get('gratis_dias', [])) == 7 else f'Grátis ({NOMES[d]})') if gratis else p['price']
        link = p.get('website') or p.get('instagram') or ''
        linhas.append({
            'id': 'museu-' + p['id'], 'data': data, 'categoria': 'Exposição', 'horario': horario,
            'nome': p['name'], 'local': p['name'], 'endereco': f"{p['address']}, {p['neighborhood']}",
            'cidade': p['city'], 'preco': preco, 'gratis': gratis, 'link': link,
            'fonte': 'Cadastro de lugares', 'fonte_link': link,
            'aviso': '' if p['situacao'] == 'aberto' else p['status'],
        })
    return linhas


if __name__ == '__main__':
    dados = carregar()
    if len(sys.argv) >= 2 and sys.argv[1] == 'validar':
        erros = validar(dados)
        print('\n'.join(erros) if erros else f"OK: {len(dados['places'])} lugares")
        sys.exit(1 if erros else 0)
    if len(sys.argv) >= 3 and sys.argv[1] == 'abertos':
        pular = set(sys.argv[4].split(',')) if len(sys.argv) >= 5 and sys.argv[3] == '--pular' else set()
        print(json.dumps(abertos(dados, sys.argv[2], pular), ensure_ascii=False, indent=1))
        sys.exit(0)
    print(__doc__)
