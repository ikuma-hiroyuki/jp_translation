# Design Document: Markdown Translator

## Overview

Markdown Translatorは、指定されたディレクトリ配下のMarkdownファイルをGCP Gemini APIを使用して日本語に翻訳するPythonコマンドラインアプリケーションです。このアプリケーションは、ディレクトリ構造を保持しながら翻訳結果を整理して保存し、エラーハンドリングとログ機能を提供します。

### 主要機能

- コマンドライン引数によるディレクトリ指定
- 再帰的なMarkdownファイル検出
- GCP Gemini APIを使用した高品質な翻訳
- Markdown形式の保持
- 脚注の翻訳除外
- ディレクトリ構造を保持した出力
- 包括的なエラーハンドリングとログ

### 技術スタック

- **言語**: Python 3.13+
- **パッケージマネージャー**: uv
- **翻訳API**: GCP Gemini API (Generative Language API)
- **主要ライブラリ**:
  - `google-generativeai`: GCP Gemini APIクライアント
  - `python-dotenv`: 環境変数管理
  - `pathlib`: ファイルシステム操作

## Architecture

### システムアーキテクチャ

アプリケーションは、関心の分離原則に基づいて以下のレイヤーに分割されます：

```
┌─────────────────────────────────────┐
│     CLI Interface Layer             │
│  (引数解析、エントリーポイント)      │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   Orchestration Layer               │
│  (翻訳プロセス全体の調整)            │
└──────────────┬──────────────────────┘
               │
       ┌───────┴────────┐
       │                │
┌──────▼─────┐   ┌─────▼──────┐
│  File      │   │ Translation│
│  System    │   │  Service   │
│  Service   │   │            │
└────────────┘   └──────┬─────┘
                        │
                 ┌──────▼─────┐
                 │  API       │
                 │  Client    │
                 └────────────┘
```

### コンポーネント概要

1. **CLI Interface**: コマンドライン引数の解析とバリデーション
2. **Orchestrator**: ファイル検出、翻訳、保存の全体フローを調整
3. **File System Service**: ファイル検出、読み込み、書き込み操作
4. **Translation Service**: 翻訳ロジックとMarkdown処理
5. **API Client**: GCP Gemini APIとの通信

## Components and Interfaces

### 1. CLI Interface (`main.py`)

**責務**: コマンドライン引数の解析とアプリケーションのエントリーポイント

```python
def main() -> int:
    """
    アプリケーションのエントリーポイント

    Returns:
        int: 終了コード（0=成功、1=エラー）
    """
    pass

def parse_arguments() -> argparse.Namespace:
    """
    コマンドライン引数を解析

    Returns:
        argparse.Namespace: 解析された引数
    """
    pass

def validate_directory(path: str) -> Path:
    """
    ディレクトリパスを検証

    Args:
        path: 検証するディレクトリパス

    Returns:
        Path: 検証済みのPathオブジェクト

    Raises:
        ValueError: ディレクトリが存在しないか、ディレクトリでない場合
    """
    pass
```

### 2. Orchestrator (`orchestrator.py`)

**責務**: 翻訳プロセス全体の調整とエラーハンドリング

```python
@dataclass
class TranslationResult:
    """翻訳結果を表すデータクラス"""
    source_file: Path
    success: bool
    error_message: Optional[str] = None

class TranslationOrchestrator:
    """翻訳プロセス全体を調整するクラス"""

    def __init__(
        self,
        file_service: FileSystemService,
        translation_service: TranslationService
    ):
        pass

    def translate_directory(self, source_dir: Path) -> list[TranslationResult]:
        """
        ディレクトリ内の全Markdownファイルを翻訳

        Args:
            source_dir: ソースディレクトリ

        Returns:
            list[TranslationResult]: 各ファイルの翻訳結果
        """
        pass

    def print_summary(self, results: list[TranslationResult]) -> None:
        """
        翻訳結果のサマリーを表示

        Args:
            results: 翻訳結果のリスト
        """
        pass
```

### 3. File System Service (`file_service.py`)

**責務**: ファイルシステム操作（検出、読み込み、書き込み）

```python
class FileSystemService:
    """ファイルシステム操作を担当するサービス"""

    def find_markdown_files(self, directory: Path) -> list[Path]:
        """
        ディレクトリ内の全Markdownファイルを再帰的に検出

        Args:
            directory: 検索対象ディレクトリ

        Returns:
            list[Path]: 検出されたMarkdownファイルのリスト
        """
        pass

    def read_file(self, file_path: Path) -> str:
        """
        ファイルの内容を読み込み

        Args:
            file_path: 読み込むファイルのパス

        Returns:
            str: ファイルの内容

        Raises:
            IOError: ファイル読み込みに失敗した場合
        """
        pass

    def write_file(self, file_path: Path, content: str) -> None:
        """
        ファイルに内容を書き込み

        Args:
            file_path: 書き込むファイルのパス
            content: 書き込む内容

        Raises:
            IOError: ファイル書き込みに失敗した場合
        """
        pass

    def create_output_path(
        self,
        source_file: Path,
        source_dir: Path,
        output_dir_name: str = "jp"
    ) -> Path:
        """
        出力ファイルのパスを生成

        Args:
            source_file: ソースファイルのパス
            source_dir: ソースディレクトリ
            output_dir_name: 出力ディレクトリ名

        Returns:
            Path: 出力ファイルのパス
        """
        pass

    def ensure_directory_exists(self, directory: Path) -> None:
        """
        ディレクトリが存在することを保証（必要に応じて作成）

        Args:
            directory: 確認/作成するディレクトリ
        """
        pass
```

### 4. Translation Service (`translation_service.py`)

**責務**: 翻訳ロジックとMarkdown処理

```python
class TranslationService:
    """翻訳処理を担当するサービス"""

    def __init__(self, api_client: GeminiAPIClient):
        self.api_client = api_client

    def translate_markdown(self, content: str) -> str:
        """
        Markdownコンテンツを日本語に翻訳

        Args:
            content: 翻訳するMarkdownコンテンツ

        Returns:
            str: 翻訳されたMarkdownコンテンツ

        Raises:
            TranslationError: 翻訳に失敗した場合
        """
        pass

    def preprocess_markdown(self, content: str) -> tuple[str, list[str]]:
        """
        Markdown前処理（脚注の抽出）

        Args:
            content: 前処理するMarkdownコンテンツ

        Returns:
            tuple[str, list[str]]: (前処理済みコンテンツ, 抽出された脚注)
        """
        pass

    def postprocess_markdown(
        self,
        translated_content: str,
        footnotes: list[str]
    ) -> str:
        """
        Markdown後処理（脚注の復元）

        Args:
            translated_content: 翻訳されたコンテンツ
            footnotes: 復元する脚注

        Returns:
            str: 後処理済みコンテンツ
        """
        pass
```

### 5. API Client (`api_client.py`)

**責務**: GCP Gemini APIとの通信

```python
class GeminiAPIClient:
    """GCP Gemini APIクライアント"""

    def __init__(self, api_key: str):
        """
        APIクライアントを初期化

        Args:
            api_key: GCP API キー

        Raises:
            ValueError: APIキーが無効な場合
        """
        pass

    def translate_text(
        self,
        text: str,
        target_language: str = "Japanese"
    ) -> str:
        """
        テキストを翻訳

        Args:
            text: 翻訳するテキスト
            target_language: ターゲット言語

        Returns:
            str: 翻訳されたテキスト

        Raises:
            APIError: API呼び出しに失敗した場合
            RateLimitError: レート制限に達した場合
        """
        pass

    @staticmethod
    def load_api_key_from_env(env_file: Path = Path(".env")) -> str:
        """
        .envファイルからAPIキーを読み込み

        Args:
            env_file: .envファイルのパス

        Returns:
            str: APIキー

        Raises:
            FileNotFoundError: .envファイルが存在しない場合
            ValueError: APIキーが見つからない場合
        """
        pass
```

### 6. Custom Exceptions (`exceptions.py`)

```python
class TranslatorError(Exception):
    """翻訳アプリケーションの基底例外"""
    pass

class TranslationError(TranslatorError):
    """翻訳処理中のエラー"""
    pass

class APIError(TranslatorError):
    """API通信エラー"""
    pass

class RateLimitError(APIError):
    """APIレート制限エラー"""
    pass
```

## Data Models

### TranslationResult

翻訳結果を表すデータクラス：

```python
@dataclass
class TranslationResult:
    """個別ファイルの翻訳結果"""
    source_file: Path          # ソースファイルのパス
    success: bool              # 翻訳が成功したか
    error_message: Optional[str] = None  # エラーメッセージ（失敗時）
```

### TranslationConfig

翻訳設定を表すデータクラス：

```python
@dataclass
class TranslationConfig:
    """翻訳設定"""
    source_directory: Path     # ソースディレクトリ
    output_directory_name: str = "jp"  # 出力ディレクトリ名
    target_language: str = "Japanese"  # ターゲット言語
    max_retries: int = 3       # 最大リトライ回数
    retry_delay: float = 1.0   # リトライ間隔（秒）
```

### ファイル構造の例

```
source_directory/
├── README.md
├── docs/
│   ├── guide.md
│   └── api.md
└── jp/                    # 出力ディレクトリ
    ├── README.md
    └── docs/
        ├── guide.md
        └── api.md
```

## Correctness Properties


*プロパティとは、システムの全ての有効な実行において真であるべき特性や動作のことです。本質的には、システムが何をすべきかについての形式的な記述です。プロパティは、人間が読める仕様と機械で検証可能な正確性保証との橋渡しとなります。*

### Property 1: Markdownファイルの完全検出

*任意の*ディレクトリ構造に対して、再帰的スキャンは全ての.md拡張子を持つファイルを検出し、検出されたファイルのリストに含める必要があります。

**Validates: Requirements 2.1**

### Property 2: APIキーの正確な抽出

*任意の*.envファイルの内容に対して、"key="形式でAPIキーが含まれている場合、そのAPIキーを正確に抽出できる必要があります。

**Validates: Requirements 3.2**

### Property 3: 全ファイルの翻訳処理

*任意の*Markdownファイルのリストに対して、各ファイルの内容が翻訳APIに送信される必要があります。

**Validates: Requirements 4.1**

### Property 4: Markdown形式の保持

*任意の*Markdownコンテンツに対して、翻訳後もMarkdown構文（見出し、リスト、コードブロック、リンクなど）が保持される必要があります。

**Validates: Requirements 4.2**

### Property 5: 脚注の翻訳除外

*任意の*脚注を含むMarkdownコンテンツに対して、脚注部分は翻訳されず、元の形式のまま出力に含まれる必要があります。

**Validates: Requirements 4.3**

### Property 6: エラー時の処理継続

*任意の*ファイルリストに対して、1つのファイルの翻訳が失敗しても、残りのファイルの処理が継続される必要があります。

**Validates: Requirements 4.4**

### Property 7: ディレクトリ構造の保持

*任意の*ソースディレクトリ構造に対して、出力ディレクトリ内で相対パス構造が保持される必要があります（例: `source/docs/guide.md` → `source/jp/docs/guide.md`）。

**Validates: Requirements 5.3**

### Property 8: エラーログの完全性

*任意の*ファイル処理エラーに対して、エラーログにはファイル名とエラー詳細の両方が含まれる必要があります。

**Validates: Requirements 6.2**

## Error Handling

### エラー分類と処理戦略

#### 1. 入力検証エラー（即座に終了）

- **無効なディレクトリパス**: ディレクトリが存在しない、またはディレクトリでない
  - エラーメッセージを表示し、終了コード1で終了

- **Markdownファイルなし**: 指定ディレクトリに.mdファイルが存在しない
  - 情報メッセージを表示し、終了コード0で終了

#### 2. 認証エラー（即座に終了）

- **.envファイルなし**: 環境ファイルが見つからない
  - エラーメッセージを表示し、終了コード1で終了

- **APIキーなし**: .envファイルにAPIキーが含まれていない
  - エラーメッセージを表示し、終了コード1で終了

- **無効なAPIキー**: APIキーが無効
  - エラーメッセージを表示し、終了コード1で終了

#### 3. ファイル処理エラー（処理継続）

- **ファイル読み込みエラー**: 個別ファイルの読み込みに失敗
  - エラーをログに記録し、次のファイルに進む
  - 最終的に終了コード1で終了

- **ファイル書き込みエラー**: 翻訳結果の書き込みに失敗
  - エラーをログに記録し、次のファイルに進む
  - 最終的に終了コード1で終了

#### 4. API通信エラー（リトライ後、処理継続）

- **一時的なネットワークエラー**: タイムアウト、接続エラー
  - 最大3回リトライ（指数バックオフ: 1秒、2秒、4秒）
  - リトライ失敗後、エラーをログに記録し、次のファイルに進む

- **レート制限エラー**: API呼び出し制限に達した
  - 60秒待機後、リトライ
  - リトライ失敗後、エラーをログに記録し、次のファイルに進む

- **APIエラー**: その他のAPIエラー
  - エラーをログに記録し、次のファイルに進む

### エラーメッセージの形式

```
[ERROR] Failed to translate file: path/to/file.md
Reason: <error_details>
```

### ログレベル

- **INFO**: 処理開始、ファイル処理開始、処理完了
- **WARNING**: リトライ実行
- **ERROR**: ファイル処理失敗、API呼び出し失敗

### 例外階層

```
TranslatorError (基底例外)
├── TranslationError (翻訳処理エラー)
├── APIError (API通信エラー)
│   └── RateLimitError (レート制限エラー)
└── FileSystemError (ファイルシステムエラー)
```

## Testing Strategy

### テスト方針

このプロジェクトでは、ユニットテストとプロパティベーステストの両方を使用して包括的なテストカバレッジを実現します。

- **ユニットテスト**: 特定の例、エッジケース、エラー条件を検証
- **プロパティベーステスト**: 全ての入力に対する普遍的なプロパティを検証

### プロパティベーステスト

**使用ライブラリ**: `hypothesis`

**設定**:
- 各プロパティテストは最低100回の反復を実行
- 各テストは対応する設計ドキュメントのプロパティを参照

**タグ形式**: `# Feature: markdown-translator, Property {number}: {property_text}`

#### プロパティテスト一覧

1. **Property 1: Markdownファイルの完全検出**
   - ランダムなディレクトリ構造を生成
   - 全ての.mdファイルが検出されることを検証
   - タグ: `# Feature: markdown-translator, Property 1: Complete Markdown file detection`

2. **Property 2: APIキーの正確な抽出**
   - ランダムな.envファイル内容を生成
   - key=形式のAPIキーが正確に抽出されることを検証
   - タグ: `# Feature: markdown-translator, Property 2: Accurate API key extraction`

3. **Property 3: 全ファイルの翻訳処理**
   - ランダムなファイルリストを生成
   - 全てのファイルが翻訳APIに送信されることを検証（モック使用）
   - タグ: `# Feature: markdown-translator, Property 3: All files translation processing`

4. **Property 4: Markdown形式の保持**
   - ランダムなMarkdownコンテンツを生成
   - 翻訳後もMarkdown構文が保持されることを検証（モック使用）
   - タグ: `# Feature: markdown-translator, Property 4: Markdown format preservation`

5. **Property 5: 脚注の翻訳除外**
   - 脚注を含むランダムなMarkdownを生成
   - 脚注が翻訳されないことを検証
   - タグ: `# Feature: markdown-translator, Property 5: Footnote translation exclusion`

6. **Property 6: エラー時の処理継続**
   - 一部のファイルで失敗するシナリオを生成
   - 残りのファイルが処理されることを検証
   - タグ: `# Feature: markdown-translator, Property 6: Processing continuation on error`

7. **Property 7: ディレクトリ構造の保持**
   - ランダムなディレクトリ構造を生成
   - 出力ディレクトリで相対パスが保持されることを検証
   - タグ: `# Feature: markdown-translator, Property 7: Directory structure preservation`

8. **Property 8: エラーログの完全性**
   - ランダムなエラーシナリオを生成
   - エラーログにファイル名とエラー詳細が含まれることを検証
   - タグ: `# Feature: markdown-translator, Property 8: Error log completeness`

### ユニットテスト

ユニットテストは特定の例とエッジケースに焦点を当てます。

#### CLI Interface Tests

- コマンドライン引数の解析
- 存在しないディレクトリの検証エラー
- ファイルパスをディレクトリとして渡した場合のエラー

#### File System Service Tests

- .mdファイルが存在しないディレクトリの処理
- 既存の出力ディレクトリの処理
- ファイル読み込み/書き込みエラーのハンドリング

#### API Client Tests

- .envファイルが存在しない場合のエラー
- APIキーが含まれていない.envファイルのエラー
- APIレート制限のハンドリング（モック使用）

#### Translation Service Tests

- 空のMarkdownコンテンツの処理
- 脚注のみのMarkdownの処理
- 複数の脚注を含むMarkdownの処理

#### Orchestrator Tests

- 全ファイル成功時の終了コード0
- 一部ファイル失敗時の終了コード1
- サマリー表示の内容検証

### テストディレクトリ構造

```
tests/
├── unit/
│   ├── test_cli.py
│   ├── test_file_service.py
│   ├── test_translation_service.py
│   ├── test_api_client.py
│   └── test_orchestrator.py
├── property/
│   ├── test_file_detection_property.py
│   ├── test_api_key_extraction_property.py
│   ├── test_translation_processing_property.py
│   ├── test_markdown_preservation_property.py
│   ├── test_footnote_exclusion_property.py
│   ├── test_error_continuation_property.py
│   ├── test_directory_structure_property.py
│   └── test_error_logging_property.py
└── fixtures/
    ├── sample_markdown/
    └── sample_env/
```

### テスト実行

```bash
# 全テスト実行
uv run pytest

# ユニットテストのみ
uv run pytest tests/unit/

# プロパティテストのみ
uv run pytest tests/property/

# カバレッジレポート
uv run pytest --cov=src --cov-report=html
```

### モックとフィクスチャ

- **GCP Gemini API**: `unittest.mock`を使用してモック化
- **ファイルシステム**: `pytest`の`tmp_path`フィクスチャを使用
- **環境変数**: `monkeypatch`フィクスチャを使用

### 継続的インテグレーション

- 全てのプルリクエストでテストを自動実行
- テストカバレッジ80%以上を維持
- プロパティテストの失敗は即座に修正
