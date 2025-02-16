#!/bin/bash

INPUT_FOLDER="./pdfs/split_pages"
OUTPUT_FOLDER="./jsons"

mkdir -p "$OUTPUT_FOLDER"

while read -r pdf_file; do
    pdf_name=$(basename "$pdf_file" .pdf)
    uv run ./parser.py "$pdf_file"
done < <(find "$INPUT_FOLDER" -type f -name "*.pdf")

echo "✅ 全てのPDFをJSONに変換しました！"
