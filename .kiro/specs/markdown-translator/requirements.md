# Requirements Document

## Introduction

Markdownファイル翻訳アプリは、指定されたディレクトリ配下のMarkdownファイルを日本語に翻訳し、翻訳結果を整理して保存するPythonアプリケーションです。GCP Gemini APIを使用して高品質な翻訳を提供します。

## Glossary

- **Translator**: Markdownファイルを翻訳するPythonアプリケーション
- **Source_Directory**: ユーザーが指定する翻訳対象のMarkdownファイルが格納されているディレクトリ
- **Output_Directory**: 翻訳されたファイルを格納する"jp"という名前のディレクトリ
- **GCP_API**: Google Cloud Platform Gemini API（Generative Language API）
- **Environment_File**: 認証情報を格納する.envファイル
- **Footnote**: Markdownファイル内の脚注文字列（翻訳対象外）
- **Markdown_File**: .md拡張子を持つファイル

## Requirements

### Requirement 1: ディレクトリ指定

**User Story:** As a ユーザー, I want コマンドライン引数でディレクトリを指定する, so that 翻訳対象のMarkdownファイルの場所を柔軟に指定できる

#### Acceptance Criteria

1. WHEN the Translator is executed, THE Translator SHALL accept a directory path as a command-line argument
2. IF the specified directory does not exist, THEN THE Translator SHALL display an error message and terminate
3. THE Translator SHALL validate that the provided path is a directory

### Requirement 2: Markdownファイルの検出

**User Story:** As a ユーザー, I want 指定ディレクトリ配下の全ての.mdファイルを自動検出する, so that 手動でファイルを指定する手間を省ける

#### Acceptance Criteria

1. THE Translator SHALL recursively scan the Source_Directory for all files with .md extension
2. THE Translator SHALL collect all discovered Markdown_File paths for processing
3. IF no Markdown_File is found, THEN THE Translator SHALL display a message and terminate gracefully

### Requirement 3: GCP API認証

**User Story:** As a ユーザー, I want .envファイルから認証情報を読み込む, so that APIキーを安全に管理できる

#### Acceptance Criteria

1. THE Translator SHALL read the Environment_File from the current working directory
2. THE Translator SHALL extract the API key using the "key=" format
3. IF the Environment_File does not exist, THEN THE Translator SHALL display an error message and terminate
4. IF the API key is not found in the Environment_File, THEN THE Translator SHALL display an error message and terminate
5. THE Translator SHALL authenticate with GCP_API using the extracted API key

### Requirement 4: 翻訳処理

**User Story:** As a ユーザー, I want Markdownファイルを日本語に翻訳する, so that 日本語話者が内容を理解できる

#### Acceptance Criteria

1. FOR EACH Markdown_File, THE Translator SHALL send the file content to GCP_API for translation to Japanese
2. THE Translator SHALL preserve Markdown formatting in the translated output
3. THE Translator SHALL exclude Footnote text from translation
4. WHEN translation fails for a file, THE Translator SHALL log the error and continue processing remaining files
5. THE Translator SHALL handle API rate limits appropriately

### Requirement 5: 出力ディレクトリ管理

**User Story:** As a ユーザー, I want 翻訳結果を"jp"ディレクトリに保存する, so that 元ファイルと翻訳ファイルを整理して管理できる

#### Acceptance Criteria

1. THE Translator SHALL create an Output_Directory named "jp" within the Source_Directory
2. IF the Output_Directory already exists, THE Translator SHALL use the existing directory
3. THE Translator SHALL preserve the relative directory structure of source files within the Output_Directory
4. FOR EACH translated Markdown_File, THE Translator SHALL save the output with the same filename in the corresponding location within the Output_Directory

### Requirement 6: エラーハンドリングとログ

**User Story:** As a ユーザー, I want 処理状況とエラーを確認できる, so that 問題が発生した際にトラブルシューティングできる

#### Acceptance Criteria

1. THE Translator SHALL display progress information for each file being processed
2. WHEN an error occurs during file processing, THE Translator SHALL log the error with the filename and error details
3. WHEN translation completes, THE Translator SHALL display a summary of successful and failed translations
4. THE Translator SHALL return a non-zero exit code if any errors occurred during execution

### Requirement 7: Python環境とパッケージ管理

**User Story:** As a 開発者, I want uvを使用してプロジェクトを管理する, so that 依存関係を適切に管理できる

#### Acceptance Criteria

1. THE Translator SHALL be compatible with Python uv package manager
2. THE Translator SHALL define all dependencies in a pyproject.toml file
3. THE Translator SHALL include the GCP Generative Language API client library as a dependency
4. THE Translator SHALL include python-dotenv library for Environment_File parsing
