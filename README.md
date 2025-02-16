# eff-models

## Tables Structure
See `20250216001144_init.sql`

## Installation
```bash
uv pip install -r requirements.txt
```

Use `google-cloud-vision` for OCR.
Download `serviceaccount.json` from [Google Cloud Console](https://console.cloud.google.com/apis/credentials).



## Parsing PDF to JSON one by one
```bash
uv run./parser.py <PDF_PATH>
```
output will be `output_<PDF_NAME>.json` and stored in `jsons` folder.

## Parsing PDFs to JSONs
```bash
./parse_all.sh
```

## Analysis
See `analysis.ipynb` for details.
