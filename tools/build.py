"""Build the search site from data/rows.json.

Usage: python3 -I tools/build.py

Outputs:
  data/komoditas.json         compact dataset used by the page
  index.html                  self-contained page (data inlined, works offline)
  dist/artifact/index.html    page fragment that fetches komoditas.json
  dist/artifact/komoditas.json
"""
import collections
import json
import pathlib
import shutil

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE_OFFSET = 8  # printed page = PDF page - 8


def build_data(rows):
    groups = collections.OrderedDict()
    for page, kel, sub, kls, kom, nama, kq, nq, level in rows:
        if level != "KOMODITAS":
            continue
        key = (kel, sub, kls, kom, nama)
        g = groups.setdefault(key, {"p0": page, "p1": page, "q": []})
        g["p1"] = page
        g["q"].append([kq, nq])

    # Level letters: G = kelompok, S = subkelompok, C = kelas.
    letter = {"KELOMPOK": "G", "SUBKELOMPOK": "S", "KELAS": "C"}
    hier = [[kel, sub, kls, nama, letter[lv]] for (page, kel, sub, kls, kom, nama, _, _, lv)
            in rows if lv != "KOMODITAS"]

    code_count = collections.Counter(k[:4] for k in groups)
    items = []
    for (kel, sub, kls, kom, nama), g in groups.items():
        flags = []
        if code_count[(kel, sub, kls, kom)] > 1:
            flags.append("dupkom")
        qcodes = [q[0] for q in g["q"]]
        if len(set(qcodes)) != len(qcodes):
            flags.append("dupq")
        items.append([kel, sub, kls, kom, nama,
                      g["p0"] - PAGE_OFFSET, g["p1"] - PAGE_OFFSET, g["q"], flags])
    return {
        "source": "Buku 5 Master Kode Komoditas dan Kualitas SPKRT 2027 (versi 2026.10.23)",
        "hier": hier,
        "items": items,
    }


def main():
    rows = json.loads((ROOT / "data/rows.json").read_text())
    data = build_data(rows)
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    (ROOT / "data/komoditas.json").write_text(payload)

    template = (ROOT / "src/page.html").read_text()
    inline = "<script>window.__SPKRT__=" + payload.replace("</", "<\\/") + ";</script>"
    standalone = (
        '<!doctype html>\n<html lang="id">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        "</head>\n<body>\n" + template.replace("<!--DATA-->", inline) + "\n</body>\n</html>\n"
    )
    (ROOT / "index.html").write_text(standalone)

    dist = ROOT / "dist/artifact"
    dist.mkdir(parents=True, exist_ok=True)
    (dist / "index.html").write_text(template.replace("<!--DATA-->", ""))
    shutil.copy(ROOT / "data/komoditas.json", dist / "komoditas.json")

    n_q = sum(len(i[7]) for i in data["items"])
    print(f"{len(data['items'])} komoditas, {n_q} kualitas, {len(payload) / 1e6:.2f} MB")


if __name__ == "__main__":
    main()
