# ai-pii-demo

Azure AI Language の PII マスキングを試せる Flask サンプルです。

現在の主要構成:

- `src/app.py`
- `src/templates/`
- `src/static/`

## 前提

- Windows
- PowerShell
- Python 3.10+
- Azure AI Language の `Endpoint` と `Key`

## 環境設定 (PowerShell)

```powershell
# 1) プロジェクトに移動
Set-Location ".\ai-pii-demo"

# 2) 仮想環境を作成
py -3.11 -m venv .venv

# 3) 仮想環境を有効化
.\.venv\Scripts\Activate.ps1

# 4) 依存パッケージをインストール
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 環境変数の設定 (.env)

`python-dotenv` を使っているので、プロジェクト直下に `.env` を作成します。

```powershell
@'
AZURE_LANGUAGE_ENDPOINT=https://<your-language-resource-name>.cognitiveservices.azure.com/
AZURE_LANGUAGE_KEY=<your-api-key>
FLASK_DEBUG=true
'@ | Set-Content -Path .env -Encoding utf8
```

## 実行方法 (PowerShell)

```powershell
# 仮想環境が未有効なら有効化
.\.venv\Scripts\Activate.ps1

# アプリ起動
python .\src\app.py
```

起動後、ブラウザで以下にアクセス:

- http://127.0.0.1:5000/

## 補足

- 一時的に環境変数を直接設定して実行したい場合:

```powershell
$env:AZURE_LANGUAGE_ENDPOINT = "https://<your-language-resource-name>.cognitiveservices.azure.com/"
$env:AZURE_LANGUAGE_KEY = "<your-language-key>"
$env:FLASK_DEBUG = "true"
python .\src\app.py
```