# product-name-matcher

Finds the same products in two price lists (yours and a supplier's) by **similar names**, and tells you how sure it is. Python standard library only.

## What it does
- Reads two CSV files and compares product names. Case, punctuation, word order, the Ukrainian/Russian letters і/и ї/и є/е ё/е ы/и and apostrophes are ignored; sizes such as `40 х 30`, `40x30 см`, `26×30x16,5` are compared as sizes.
- Every row of list A gets a status:
  - `match`: score 0.80 or higher,
  - `review`: score from 0.55 to 0.80, **check it by hand**,
  - `no_match`: no partner found.
- A **different size never gives an automatic match**: the score is lowered so that such pairs go to `review`.
- Each product of list B is used at most once (best scores first). Items that exist only in list B are counted in the summary.
- Writes `matches.csv` with `status, score, a, b`.

## Use
```bash
PYTHONPATH=src python3 -m name_matcher examples/shop.csv examples/supplier.csv --col-a name --col-b name --out matches.csv
```
`--hi` and `--lo` change the thresholds. Tests: `python3 -m unittest discover -s tests`.

## Limits (read this)
- It compares **spelling**, not meaning. It does not translate: "Игрушка" and "Іграшка" score low; "м'яч" and "мяч" score high.
- The score is a heuristic (word overlap and character similarity), not a probability. Always read the `review` rows. Check a sample of `match` rows before a bulk import.
- Only names are used, not brands, SKUs or prices. Two different products with the same words and sizes can look identical.
- It is quadratic (every A name against every B name): fine for thousands of rows, slow for hundreds of thousands.

MIT license.

---

# product-name-matcher (українською)

Знаходить однакові товари у двох прайсах за **схожими назвами** і показує, наскільки впевнено. Лише стандартна бібліотека Python.

**Запуск:** `PYTHONPATH=src python3 -m name_matcher shop.csv supplier.csv --out matches.csv`. Статуси: `match` (від 0,80), `review` (0,55–0,80, перевірте вручну), `no_match`. Інший розмір ніколи не дає автоматичного збігу.

**Важливо:** порівнюється написання, а не зміст; слова не перекладаються. Оцінка — евристика, рядки `review` треба читати.
