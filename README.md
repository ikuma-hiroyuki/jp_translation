# Markdown Translator

Markdownファイルを日本語に翻訳するPythonアプリケーション。GCP Gemini APIを使用して高品質な翻訳を提供します。

## 機能

- 指定ディレクトリ配下の全.mdファイルを再帰的に検出
- GCP Gemini APIを使用した高品質な翻訳
- Markdown形式の保持
- 脚注の翻訳除外
- ディレクトリ構造を保持した出力
- エラーハンドリングとリトライロジック

## 必要要件

- Python 3.13+
- uv (パッケージマネージャー)
- GCP Gemini API キー

## インストール

```bash
# 依存関係のインストール
uv sync
```

## 設定

`.env`ファイルを作成し、APIキーを設定：

```
key=YOUR_GEMINI_API_KEY
```

### モデル名の変更（オプション）

デフォルトでは`gemini-3-flash-preview`を使用しますが、環境変数で変更可能：

```bash
export GEMINI_MODEL=gemini-3.1-pro-preview
```

または、`.env`ファイルに追加：

```
key=YOUR_GEMINI_API_KEY
GEMINI_MODEL=gemini-3.1-pro-preview
```

利用可能なモデル：
- `gemini-3-flash-preview` (デフォルト、速度とコストのバランスが良い)
- `gemini-3.1-pro-preview` (最高品質、高コスト)
- `gemini-3-pro-preview` (高品質)

## 使用方法

```bash
uv run main.py <ディレクトリパス>
```

例：
```bash
uv run main.py /path/to/markdown/files
```

翻訳されたファイルは、指定ディレクトリ内の`jp`ディレクトリに保存されます。

## 出力例

```
source_directory/
├── README.md
├── docs/
│   ├── guide.md
│   └── api.md
└── jp/                    # 翻訳結果
    ├── README.md
    └── docs/
        ├── guide.md
        └── api.md
```

## テスト

```bash
# 全テスト実行
uv run pytest

# カバレッジレポート
uv run pytest --cov=src --cov-report=html
```

## ライセンス

MIT License
