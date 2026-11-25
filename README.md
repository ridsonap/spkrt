# Master Kode SPKRT 2027

Search page for the commodity and quality codes in *Buku 5: Master Kode Komoditas dan
Kualitas SPKRT 2027* (version 2026.10.23). Search by commodity name, brand/quality name,
or code (`0111001`, `01.1.1.001`, `01.1.1.001.161`), or browse by kelompok.

Not an official BPS application. Always check codes against the printed guideline.

## Layout

- `index.html` – the site; self-contained (data inlined), works offline.
- `src/page.html` – page template.
- `data/rows.json` – raw rows extracted from the PDF.
- `data/komoditas.json` – compact dataset used by the page.
- `tools/extract.py` – PDF → `data/rows.json` (needs PyMuPDF).
- `tools/build.py` – `data/rows.json` + `src/page.html` → `index.html`.

## Rebuild

```sh
python3 -I tools/extract.py "Buku 5 Master Kode Komoditas dan Kualitas SPKRT 2027.pdf" data/rows.json
python3 -I tools/build.py
```

`extract.py` aborts if the number of extracted rows on any page differs from the number
of level labels in that page's raw text.

## Known issues in the source book

- `06.2.2.005` quality `002` is used twice (SPBKLU and SPKLU), book page 469.
- `11.9.1.031` is used for two commodities (JASTIP BARANG and KOMODITAS LAINNYA), book page 569.

Both are flagged on the page.
