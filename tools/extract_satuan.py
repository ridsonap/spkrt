"""Extract standard units (satuan standar) from the SPKRT 2027 food worksheet
questionnaire "Kuesioner VPKRT27-LK" (PDF).

Usage: python3 -I tools/extract_satuan.py <VPKRT27-LK.pdf> data/satuan.json

Output: {kode_komoditas_7_digit: [satuan_standar, jenis_barang, pdf_page]}.
An empty satuan means the questionnaire row has no unit (e.g. milling services).
"""
import json
import re
import sys

import pymupdf

CODE = re.compile(r"\d{7}")


def main(pdf_path, out_path):
    doc = pymupdf.open(pdf_path)
    out = {}
    raw_codes = 0
    for i in range(doc.page_count):
        raw_codes += len(re.findall(r"(?m)^\s*\d{7}\b", doc[i].get_text()))
        for table in doc[i].find_tables().tables:
            for r in table.extract():
                cells = [(c or "").replace("\n", " ").strip() for c in r]
                cells = [c for c in cells if c]
                if not cells or not CODE.fullmatch(cells[0]):
                    continue
                # Row shape: code, jenis barang, "Pembelian", satuan standar.
                code, name = cells[0], re.sub(r"\s+", " ", cells[1])
                if len(cells) == 4 and cells[2] == "Pembelian":
                    unit = cells[3]
                elif len(cells) == 3 and cells[2] == "Pembelian":
                    unit = ""
                else:
                    sys.exit(f"page {i + 1}: unexpected row {cells}")
                if code in out:
                    sys.exit(f"page {i + 1}: duplicate code {code}")
                out[code] = [unit, name, i + 1]

    # Every 7-digit code in the raw text must come out of a table row.
    if raw_codes != len(out):
        sys.exit(f"{raw_codes} codes in text, {len(out)} extracted")

    with open(out_path, "w") as f:
        json.dump(out, f, ensure_ascii=False, indent=0)
    print(len(out), "codes,", sum(1 for v in out.values() if v[0]), "with satuan")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
