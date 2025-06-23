# CLAUDE.md 分割移行計画

## 📊 現在の構成分析

**総行数**: 679行
**主要セクション**: 8セクション

## 🎯 分割マッピング

### development/ ディレクトリ
| 移行先ファイル | 元セクション | 行範囲 |
|---------------|-------------|--------|
| `quick-start.md` | ## 開発コマンド | 5-49 |
| `coding-standards.md` | ## 開発ガイドライン | 262-337 |
| `environment-config.md` | 環境変数管理部分 | 563-以降 |
| `debugging.md` | デバッグ関連 | 563-以降から抽出 |

### architecture/ ディレクトリ
| 移行先ファイル | 元セクション | 行範囲 |
|---------------|-------------|--------|
| `overview.md` | ## アーキテクチャ概要 | 50-109 |
| `adk-first-design.md` | ADK統合部分 | 50-109から抽出 |
| `clean-architecture.md` | 設計パターン | 50-109から抽出 |
| `di-container-design.md` | ## 高度なアーキテクチャパターン | 379-442 |

### guides/ ディレクトリ
| 移行先ファイル | 元セクション | 行範囲 |
|---------------|-------------|--------|
| `new-agent-creation.md` | ## 一般的な開発ワークフロー | 110-261 |
| `new-tool-development.md` | ツール開発部分 | 110-261から抽出 |
| `troubleshooting.md` | ## 重要な実装パターン | 443-562 |

### technical/ ディレクトリ
| 移行先ファイル | 元セクション | 行範囲 |
|---------------|-------------|--------|
| `adk-best-practices.md` | ADK制約部分 | 50-109から抽出 |
| `error-handling.md` | エラーハンドリング | 443-562から抽出 |
| `logging-monitoring.md` | ログ・監視 | 262-337から抽出 |

## 🔍 Context7ライブラリ参照の処理

**Line 338-378**: ## Context7ライブラリ参照
→ `technical/library-integration.md` として独立

## ⚠️ 重複コンテンツの統合

以下のセクションには重複する内容があるため、統合が必要：
- 開発ガイドライン (Line 262)
- 重要な開発ガイドライン (Line 563)
→ `development/coding-standards.md` に統合

## 📋 Phase 3 実行順序

1. **development/quick-start.md** (Line 5-49)
2. **architecture/overview.md** (Line 50-109) 
3. **guides/new-agent-creation.md** (Line 110-261)
4. **development/coding-standards.md** (Line 262-337 + 563-以降)
5. **technical/library-integration.md** (Line 338-378)
6. **architecture/di-container-design.md** (Line 379-442)
7. **guides/troubleshooting.md** (Line 443-562)

## 🎯 新しいCLAUDE.md構成

**軽量エントリーポイント** (約50行):
- プロジェクト概要
- 目的別クイックリンク
- 各docsディレクトリへの誘導