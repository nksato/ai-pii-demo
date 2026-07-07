import os

from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

load_dotenv()

app = Flask(__name__)

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
    categories: list[str] = data.get("categories", [])

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
    except EnvironmentError as exc:
        return jsonify({"error": str(exc)}), 500

    try:
        results = client.recognize_pii_entities(
            [text],
            language="ja",
            categories_filter=selected_categories,
        )
    except Exception as exc:  # noqa: BLE001
        return jsonify({"error": f"Azure API エラー: {exc}"}), 502

    for doc in results:
        if doc.is_error:
            return jsonify(
                {"error": f"ドキュメント処理エラー: {doc.error.message}"}
            ), 502
        return jsonify({"masked_text": doc.redacted_text})

    return jsonify({"masked_text": text})


if __name__ == "__main__":
    app.run(debug=True)
