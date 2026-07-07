import logging
import os
from typing import List

from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import AzureError
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

load_dotenv()

app = Flask(__name__)
logger = logging.getLogger(__name__)

# Mapping from frontend category keys to Azure PII entity category strings
CATEGORY_MAP = {
    "name": "Person",
    "phone": "PhoneNumber",
    "address": "Address",
    "email": "Email",
}


def get_text_analytics_client() -> TextAnalyticsClient:
    endpoint = os.environ.get("AZURE_LANGUAGE_ENDPOINT", "")
    key = os.environ.get("AZURE_LANGUAGE_KEY", "")
    if not endpoint or not key:
        raise EnvironmentError(
            "AZURE_LANGUAGE_ENDPOINT and AZURE_LANGUAGE_KEY must be set."
        )
    return TextAnalyticsClient(endpoint=endpoint, credential=AzureKeyCredential(key))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json(silent=True) or {}
    text: str = data.get("text", "").strip()
    categories: List[str] = data.get("categories", [])

    if not text:
        return jsonify({"error": "テキストを入力してください。"}), 400

    if not categories:
        return jsonify({"error": "検出する項目を少なくとも1つ選択してください。"}), 400

    # Resolve selected category strings understood by the Azure API
    selected_categories = [
        CATEGORY_MAP[c] for c in categories if c in CATEGORY_MAP
    ]
    if not selected_categories:
        return jsonify({"error": "有効な検出項目が選択されていません。"}), 400

    try:
        client = get_text_analytics_client()
    except EnvironmentError:
        return jsonify({"error": "AZURE_LANGUAGE_ENDPOINT と AZURE_LANGUAGE_KEY を設定する必要があります。"}), 500

    try:
        results = client.recognize_pii_entities(
            [text],
            language="ja",
            categories_filter=selected_categories,
        )
    except AzureError:
        logger.exception(
            "Azure API call failed (categories=%s, text_length=%d)",
            selected_categories,
            len(text),
        )
        return jsonify({"error": "Azure API の呼び出しに失敗しました。しばらく経ってから再試行してください。"}), 502

    # We always send exactly one document, so take the first result.
    doc = results[0]
    if doc.is_error:
        logger.error("PII recognition error: code=%s message=%s", doc.error.code, doc.error.message)
        return jsonify({"error": "テキストの処理中にエラーが発生しました。入力を確認してください。"}), 502

    return jsonify({"masked_text": doc.redacted_text})


if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG", "false").lower() == "true")
