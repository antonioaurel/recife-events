#!/usr/bin/env python3
"""Gera data/hoje.json e data/proximos.json a partir de data/instagram.json.

- hoje.json: eventos do Instagram que acontecem hoje (fuso America/Recife),
  incluindo os que estão em cartaz no período (data <= hoje <= data_fim).
- proximos.json: eventos do Instagram a partir de amanhã (e os em cartaz que
  continuam depois de hoje), mais os itens de outras fontes que já estavam no
  arquivo e ainda não passaram. Itens gerados por este script levam
  "origem": "instagram" e são recriados a cada execução.
- meta.json: carimbo de atualização.

Uso: python3 tools/instagram_para_agenda.py
"""
import datetime
import json
import re
from pathlib import Path
from zoneinfo import ZoneInfo

DATA = Path(__file__).resolve().parent.parent / "data"
CATEGORIA = {
    "Feiras": "Feira",
    "Eventos gerais": "Evento",
    "Teatro": "Teatro",
    "Museus e exposições": "Exposição",
    "Cinema": "Cinema",
    "Shows e festas": "Show",
    "Parques": "Parque",
}


# Bairro de locais conhecidos (quando o texto do local não traz o bairro).
BAIRRO_LOCAL = {
    "caixa cultural": "Bairro do Recife", "cais do sertao": "Bairro do Recife", "marco zero": "Bairro do Recife",
    "paco do frevo": "Bairro do Recife", "mirante do paco": "Bairro do Recife", "rua do bom jesus": "Bairro do Recife",
    "teatro hermilo": "Bairro do Recife", "teatro apolo": "Bairro do Recife", "torre malakoff": "Bairro do Recife",
    "kahal zur": "Bairro do Recife", "forte do brum": "Bairro do Recife", "bonecos gigantes": "Bairro do Recife",
    "teatro de santa isabel": "Santo Antônio", "cinema sao luiz": "Boa Vista", "teatro do parque": "Boa Vista",
    "clube internacional": "Boa Vista", "mamam": "Boa Vista", "rua do hospicio": "Boa Vista",
    "museu da cidade do recife": "São José", "cinco pontas": "São José", "museu do trem": "São José",
    "estacao central": "São José", "galo da madrugada": "São José",
    "museu do estado": "Graças", "museu da abolicao": "Madalena", "murillo la greca": "Parnamirim",
    "instituto ricardo brennand": "Várzea", "pinacoteca do instituto ricardo brennand": "Várzea",
    "oficina francisco brennand": "Várzea", "oficina ceramica francisco brennand": "Várzea",
    "ufpe": "Cidade Universitária", "cidade universitaria": "Cidade Universitária",
    "parque apipucos": "Apipucos", "parque da jaqueira": "Jaqueira", "parque dona lindu": "Boa Viagem",
    "pracinha de boa viagem": "Boa Viagem", "amparo 60": "Boa Viagem", "teatro riomar": "Pina",
    "moviemax rosa e silva": "Aflitos", "clube nautico": "Aflitos", "geraldao": "Imbiribeira",
    "casa estacao da luz": "Carmo", "mac-pe": "Carmo", "eufrasio barbosa": "Varadouro",
    "teatro fernando santa cruz": "Varadouro", "museu regional de olinda": "Amparo",
    "classic hall": "Salgadinho", "centro de convencoes": "Salgadinho",
}
# Bairros que podem aparecer escritos no próprio local/endereço.
BAIRROS = ["Bairro do Recife", "Recife Antigo", "Boa Viagem", "Boa Vista", "Santo Antônio", "Santo Amaro", "São José",
    "Casa Forte", "Casa Amarela", "Poço da Panela", "Graças", "Espinheiro", "Aflitos", "Derby", "Madalena", "Torre",
    "Parnamirim", "Jaqueira", "Tamarineira", "Apipucos", "Várzea", "Cidade Universitária", "Ipsep", "Imbiribeira",
    "Pina", "Afogados", "Encruzilhada", "Rosarinho", "Ilha do Leite", "Ilha do Retiro", "Cordeiro", "Iputinga",
    "Carmo", "Varadouro", "Amparo", "Alto da Sé", "Salgadinho", "Bonsucesso", "Rio Doce", "Casa Caiada", "Bairro Novo",
    "Piedade", "Candeias"]


def sem_acento(t):
    import unicodedata
    return unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()


def achar_bairro(texto, lugar=None, cidade=""):
    t = sem_acento(texto or "")
    for chave, b in sorted(BAIRRO_LOCAL.items(), key=lambda kv: -len(kv[0])):
        if chave in t:
            return b
    for b in sorted(BAIRROS, key=len, reverse=True):
        if re.search(r"\b" + re.escape(sem_acento(b)) + r"\b", t):
            return "Bairro do Recife" if b == "Recife Antigo" else b
    # Por último, o bairro do lugar cadastrado, se o evento for na mesma cidade.
    if lugar and lugar.get("neighborhood") and (not cidade or lugar.get("city", "") == cidade):
        return lugar["neighborhood"]
    return ""


def ler(nome):
    p = DATA / nome
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else []


def gravar(nome, obj):
    (DATA / nome).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def converter(e, lugares):
    nome = e["nome"]
    cat = "Aviso" if nome.startswith("Aviso:") else CATEGORIA.get(e["eixo"], "Evento")
    item = {
        "id": "ig-" + e["id"],
        "data": e["data"],
        "categoria": cat,
        "horario": e.get("horario", ""),
        "nome": nome,
        "local": e.get("local", ""),
        "endereco": "",
        "bairro": e.get("bairro") or achar_bairro(e.get("local", ""), lugares.get(e.get("lugar_id", "")), e.get("cidade", "")),
        "cidade": e.get("cidade", "") or "Recife",
        "preco": e.get("preco", ""),
        "gratis": e.get("gratis"),
        "descricao": e.get("resumo", ""),
        "resumo": e.get("resumo", ""),
        "link": "",
        "fonte": e.get("fonte", ""),
        "fonte_link": e.get("fonte_link", ""),
        "origem": "instagram",
    }
    if e.get("data_fim"):
        item["data_fim"] = e["data_fim"]
    return item


def main():
    agora = datetime.datetime.now(ZoneInfo("America/Recife"))
    hoje = agora.date().isoformat()
    lug = ler("lugares.json")
    lugares = {p["id"]: p for p in (lug.get("places", []) if isinstance(lug, dict) else [])}
    ig = [converter(e, lugares) for e in ler("instagram.json").get("eventos", [])]
    fim = lambda r: r.get("data_fim") or r["data"]

    em_hoje = []
    for r in ig:
        if r["data"] <= hoje <= fim(r):
            x = dict(r, data=hoje)
            em_hoje.append(x)
    em_hoje.sort(key=lambda r: (r["categoria"] == "Aviso", "data_fim" in r, r["horario"], r["nome"]))

    futuros = [r for r in ig if fim(r) > hoje]
    outros = [r for r in ler("proximos.json") if r.get("origem") != "instagram" and fim(r) >= hoje]
    vistos = {(r["nome"].lower(), r["data"]) for r in futuros}
    outros = [r for r in outros if (r["nome"].lower(), r["data"]) not in vistos]
    for r in outros:
        if not r.get("bairro"):
            r["bairro"] = achar_bairro(" ".join([r.get("local", ""), r.get("endereco", "")]))
    proximos = sorted(futuros + outros, key=lambda r: (r["data"], r.get("horario", ""), r["nome"]))

    gravar("hoje.json", em_hoje)
    gravar("proximos.json", proximos)
    gravar("meta.json", {"updated": agora.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")})
    print(f"hoje.json: {len(em_hoje)} | proximos.json: {len(proximos)} ({len(futuros)} do Instagram, {len(outros)} de outras fontes)")


if __name__ == "__main__":
    main()
