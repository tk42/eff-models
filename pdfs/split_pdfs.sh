#!/bin/bash

INPUT_FOLDER="./"  # ここをPDFのフォルダに変更
OUTPUT_FOLDER="${INPUT_FOLDER}/split_pages"

# 出力フォルダを作成
mkdir -p "$OUTPUT_FOLDER"

# フォルダ内の全PDFを処理
find "$INPUT_FOLDER" -type f -name "*.pdf" | while read -r pdf_file; do
    pdf_name=$(basename "$pdf_file" .pdf)
    pdfseparate "$pdf_file" "$OUTPUT_FOLDER/${pdf_name}_page_%d.pdf"
done

echo "✅ 全てのPDFを1ページずつ分割しました！"