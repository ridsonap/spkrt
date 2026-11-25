"""Extract the commodity/quality code tables from
"Buku 5 Master Kode Komoditas dan Kualitas SPKRT 2027" (PDF).

Usage: python3 -I tools/extract.py <buku5.pdf> data/rows.json

Each output row: [pdf_page, kelompok, subkelompok, kelas, komoditas,
                  nama, kode_kualitas, nama_kualitas, level]
"""
import collections
import json
import sys

import pymupdf

LEVELS = {"KOMODITAS", "KELAS", "SUBKELOMPOK", "KELOMPOK"}
FIRST_TABLE_PAGE = 8  # 0-based; printed page 1 is PDF page 9


def main(pdf_path, out_path):
    doc = pymupdf.open(pdf_path)
    rows = []
    for i in range(FIRST_TABLE_PAGE, doc.page_count):
        for table in doc[i].find_tables().tables:
            for r in table.extract():
                if not r or r[0] is None:
                    continue
                r = [(c or "").replace("\n", " ").strip() for c in r]
                if r[0].startswith("Kode") or r[0] == "(1)":
                    continue
                if len(r) != 8:
                    sys.exit(f"page {i + 1}: unexpected row {r}")
                rows.append([i + 1] + r)

    # Cross-check: every level label in the raw text must yield one row.
    per_page = collections.Counter(r[0] for r in rows)
    for i in range(FIRST_TABLE_PAGE, doc.page_count):
        raw = sum(1 for line in doc[i].get_text().split("\n") if line.strip() in LEVELS)
        if raw != per_page.get(i + 1, 0):
            sys.exit(f"page {i + 1}: {raw} rows in text, {per_page.get(i + 1, 0)} extracted")

    with open(out_path, "w") as f:
        json.dump(rows, f, ensure_ascii=False)
    print(len(rows), "rows", collections.Counter(r[8] for r in rows))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
