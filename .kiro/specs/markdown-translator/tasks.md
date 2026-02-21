# Implementation Plan: Markdown Translator

## Overview

Pythonを使用してMarkdownファイル翻訳アプリケーションを実装します。GCP Gemini APIを使用し、ディレクトリ構造を保持しながら翻訳結果を整理して保存します。uvパッケージマネージャーを使用してプロジェクトを管理します。

## Tasks

- [x] 1. プロジェクトのセットアップと基本構造の作成
  - uvを使用してPythonプロジェクトを初期化
  - pyproject.tomlに依存関係を定義（google-generativeai, python-dotenv）
  - ディレクトリ構造を作成（src/, tests/unit/, tests/property/, tests/fixtures/）
  - カスタム例外クラスを定義（exceptions.py）
  - _Requirements: 7.1, 7.2, 7.3, 7.4_

- [ ] 2. API Clientの実装
  - [x] 2.1 GeminiAPIClientクラスの実装
    - __init__メソッドでAPIキーを受け取り、google.generativeaiを初期化
    - translate_textメソッドでテキスト翻訳を実装
    - load_api_key_from_envメソッドで.envファイルからAPIキーを読み込み
    - エラーハンドリング（APIError, RateLimitError）を実装
    - _Requirements: 3.2, 3.5, 4.1_

  - [ ]* 2.2 API Clientのプロパティテストを作成
    - **Property 2: APIキーの正確な抽出**
    - **Validates: Requirements 3.2**

  - [ ]* 2.3 API Clientのユニットテストを作成
    - .envファイルが存在しない場合のエラーテスト
    - APIキーが含まれていない場合のエラーテスト
    - APIレート制限のハンドリングテスト（モック使用）
    - _Requirements: 3.3, 3.4_

- [ ] 3. File System Serviceの実装
  - [x] 3.1 FileSystemServiceクラスの実装
    - find_markdown_filesメソッドで.mdファイルを再帰的に検出
    - read_fileメソッドでファイル内容を読み込み
    - write_fileメソッドでファイルに書き込み
    - create_output_pathメソッドで出力パスを生成
    - ensure_directory_existsメソッドでディレクトリを作成
    - _Requirements: 2.1, 2.2, 5.1, 5.2, 5.3, 5.4_

  - [ ]* 3.2 File System Serviceのプロパティテストを作成
    - **Property 1: Markdownファイルの完全検出**
    - **Validates: Requirements 2.1**
    - **Property 7: ディレクトリ構造の保持**
    - **Validates: Requirements 5.3**

  - [ ]* 3.3 File System Serviceのユニットテストを作成
    - .mdファイルが存在しないディレクトリの処理テスト
    - 既存の出力ディレクトリの処理テスト
    - ファイル読み込み/書き込みエラーのハンドリングテスト
    - _Requirements: 2.3_

- [ ] 4. Checkpoint - 基本サービスの動作確認
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 5. Translation Serviceの実装
  - [x] 5.1 TranslationServiceクラスの実装
    - __init__メソッドでGeminiAPIClientを受け取る
    - translate_markdownメソッドで翻訳処理全体を調整
    - preprocess_markdownメソッドで脚注を抽出
    - postprocess_markdownメソッドで脚注を復元
    - _Requirements: 4.1, 4.2, 4.3_

  - [ ]* 5.2 Translation Serviceのプロパティテストを作成
    - **Property 4: Markdown形式の保持**
    - **Validates: Requirements 4.2**
    - **Property 5: 脚注の翻訳除外**
    - **Validates: Requirements 4.3**

  - [ ]* 5.3 Translation Serviceのユニットテストを作成
    - 空のMarkdownコンテンツの処理テスト
    - 脚注のみのMarkdownの処理テスト
    - 複数の脚注を含むMarkdownの処理テスト
    - _Requirements: 4.3_

- [ ] 6. Orchestratorの実装
  - [x] 6.1 TranslationResultデータクラスの実装
    - source_file, success, error_messageフィールドを定義
    - _Requirements: 6.2_

  - [x] 6.2 TranslationOrchestratorクラスの実装
    - __init__メソッドでFileSystemServiceとTranslationServiceを受け取る
    - translate_directoryメソッドで翻訳プロセス全体を調整
    - エラーハンドリングと処理継続ロジックを実装
    - print_summaryメソッドで翻訳結果のサマリーを表示
    - _Requirements: 4.4, 6.1, 6.2, 6.3_

  - [ ]* 6.3 Orchestratorのプロパティテストを作成
    - **Property 3: 全ファイルの翻訳処理**
    - **Validates: Requirements 4.1**
    - **Property 6: エラー時の処理継続**
    - **Validates: Requirements 4.4**
    - **Property 8: エラーログの完全性**
    - **Validates: Requirements 6.2**

  - [ ]* 6.4 Orchestratorのユニットテストを作成
    - 全ファイル成功時の終了コード0のテスト
    - 一部ファイル失敗時の終了コード1のテスト
    - サマリー表示の内容検証テスト
    - _Requirements: 6.3, 6.4_

- [ ] 7. Checkpoint - コアロジックの動作確認
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 8. CLI Interfaceの実装
  - [x] 8.1 main.pyの実装
    - parse_argumentsメソッドでコマンドライン引数を解析
    - validate_directoryメソッドでディレクトリパスを検証
    - mainメソッドでアプリケーション全体を調整
    - 全コンポーネントを統合し、エントリーポイントを作成
    - _Requirements: 1.1, 1.2, 1.3_

  - [ ]* 8.2 CLI Interfaceのユニットテストを作成
    - コマンドライン引数の解析テスト
    - 存在しないディレクトリの検証エラーテスト
    - ファイルパスをディレクトリとして渡した場合のエラーテスト
    - _Requirements: 1.2, 1.3_

- [ ] 9. エラーハンドリングとリトライロジックの実装
  - [x] 9.1 API Clientにリトライロジックを追加
    - 一時的なネットワークエラーのリトライ（指数バックオフ）
    - レート制限エラーの待機とリトライ
    - 最大リトライ回数の設定
    - _Requirements: 4.5_

  - [x] 9.2 TranslationConfigデータクラスの実装
    - 翻訳設定（max_retries, retry_delayなど）を定義
    - _Requirements: 4.5_

- [ ] 10. 統合とエンドツーエンドテスト
  - [x] 10.1 全コンポーネントの統合確認
    - 実際のディレクトリ構造を使用した統合テスト
    - エラーシナリオの統合テスト
    - _Requirements: 1.1, 2.1, 3.5, 4.1, 5.3, 6.1_

  - [ ]* 10.2 エンドツーエンドのプロパティテストを作成
    - 全プロパティを統合的に検証
    - _Requirements: All_

- [x] 11. Final checkpoint - 全機能の動作確認
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- タスクに`*`が付いているものはオプションで、スキップ可能です
- 各タスクは特定の要件を参照しており、トレーサビリティを確保しています
- Checkpointタスクで段階的な検証を行います
- プロパティテストは普遍的な正確性プロパティを検証します
- ユニットテストは特定の例とエッジケースを検証します
