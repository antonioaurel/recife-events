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


def ler(nome):
    p = DATA / nome
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else []


def gravar(nome, obj):
    (DATA / nome).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def converter(e):
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
    ig = [converter(e) for e in ler("instagram.json").get("eventos", [])]
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
    proximos = sorted(futuros + outros, key=lambda r: (r["data"], r.get("horario", ""), r["nome"]))

    gravar("hoje.json", em_hoje)
    gravar("proximos.json", proximos)
    gravar("meta.json", {"updated": agora.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")})
    print(f"hoje.json: {len(em_hoje)} | proximos.json: {len(proximos)} ({len(futuros)} do Instagram, {len(outros)} de outras fontes)")


if __name__ == "__main__":
    main()
