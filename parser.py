import os
import io
import re
import json
import sys
import base64
import logging
import openai
import pdfplumber
from pydantic import BaseModel
from typing import Optional
from google.cloud import vision


logger = logging.getLogger(__name__)

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class MarketCondition(BaseModel):
    round: int
    date: str
    shipped_volume: float


class Price(BaseModel):
    tree_species: str
    diameter_class: str
    length: float
    top_diameter_min: float
    top_diameter_max: float
    price_low: float
    price_middle: Optional[float]
    price_high: float
    tone: Optional[str]
    summary: Optional[str]


class WoodPrices(BaseModel):
    market_condition: MarketCondition
    prices: list[Price]


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./serviceaccount.json"


def ocr_pdf(pdf_path, dpi=300):
    client = vision.ImageAnnotatorClient()

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            pil_image = page.to_image(resolution=dpi).original

    # PIL の画像を PNG バイト列に変換
    with io.BytesIO() as buf:
        pil_image.save(buf, format="PNG")
        img_bytes = buf.getvalue()

    # Cloud Vision へ送信
    image = vision.Image(content=img_bytes)
    response = client.document_text_detection(image=image)
    # texts = response.text_annotations
    # result = texts[0].description if texts else None
    texts = response.full_text_annotation
    result = re.sub(r'(?<!000)\n', '', texts.text)
    return result


def get_str_from_pdf(pdf_path, dpi=300):
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            pil_image = page.to_image(resolution=dpi).original
    
    # PIL の画像を PNG バイト列に変換
    with io.BytesIO() as buf:
        pil_image.save(buf, format="PNG")
        img_bytes = buf.getvalue()

    encoded_string = base64.b64encode(img_bytes).decode('utf-8')
    return encoded_string


def extract_text_from_pdf(pdf_path):
    full_text = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text.append(text)
    text = "\n".join(full_text)
    return text


def create_structured_output(text: str, image: str = None):
    # OpenAIのStructured Outputのプロンプトを作成
    system_prompt = f"""
    You are a data transformation expert. Your task is to transform the given text data {'and image' if image else ''} into a provided response format.

    Important rules for transformation:
    1. 'date' field should be in the format YYYY-MM-DD.
    
    2. 'shipped_volume' field should be a float and its unit is m^3.
    
    3. 'tree_species' field should be amoung 'スギ', 'ヒノキ', 'マツ', 'その他'
    
    4. 'diameter_class' field should be amoung '中目', '柱', '土台', '元木良材', '丁物', '登り', '長木', 'その他'. But '元木' should be skipped at located between top_diameter_max and price_low.

    """
    
    user_prompt = f"""
    Here is the sample data from the text:
    {text}
    """
    
    # OpenAIのAPIを呼び出し
    completion = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": [
                {"type": "text", "text": user_prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image}" # Use the correctly encoded string
                    }
                } if image else None,
            ]}
        ],
        response_format=WoodPrices,
    )
    
    # レスポンスを解析してJSONに変換
    try:
        content = completion.choices[0].message.parsed
        logger.info(f"Response content: {json.dumps(content.model_dump(), ensure_ascii=False, indent=2)}")
    except Exception as e:
        logger.error(f"Error parsing response: {e}")
        return None

    return content


if __name__ == "__main__":
    pdf_path = sys.argv[1]
    assert os.path.exists(pdf_path), f"PDF file not found: {pdf_path}"
    file_name = os.path.basename(pdf_path)[:-len(".pdf")]
    output_file = f"output_{file_name}.json"

    pdf_text = extract_text_from_pdf(pdf_path)

    pdf_image_base64 = None

    # 文字埋め込みされているものは既に実施済みなので終了
    if len(pdf_text.strip()) == 0:
        pdf_image_base64 = get_str_from_pdf(pdf_path)
    else:
        sys.exit(0)

    data = create_structured_output(pdf_text, image=pdf_image_base64)
    json_data = data.model_dump_json()
    print(json_data)
    with open("./jsons/"+output_file, "w") as f:
        f.write(json_data)
