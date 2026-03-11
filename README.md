# 匂わせ警察

just a joke bot.

[![Docker Hub](https://img.shields.io/badge/Docker%20Hub-Repository-2496ED?logo=docker&logoColor=white)](https://hub.docker.com/r/4nm1tsu/niowase-police)
[![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/4nm1tsu/niowase-police/cd.yml)](https://github.com/4nm1tsu/niowase-police/actions)

## 環境変数

| 変数名 | 説明 | デフォルト値 | 必須 |
|--------|------|-------------|------|
| `DISCORD_TOKEN` | DiscordのBotトークン | - | ✅ |
| `THRESHOLD` | 匂わせ検出の閾値（0.0〜1.0） | `0.2` | ❌ |
| `TARGET_CHANNEL_ID` | 監視対象のチャンネルID（0の場合は全チャンネル） | `0` | ❌ |
| `APP_VERSION` | アプリケーションのバージョン | `v1.0.0` | ❌ |
| `TIMEOUT_MINUTES` | 警告時のタイムアウト時間（分）<br>0の場合はタイムアウトなし、1以上で指定分数のタイムアウトを付与 | `0` | ❌ |

## 使い方

1. Discordで匂わせ画像を投稿すると、Botが自動で検出して警告します
2. `TIMEOUT_MINUTES`を1以上に設定すると、警告時に指定した分数のタイムアウトが付与されます
   - 例: `TIMEOUT_MINUTES=5` → 5分間のタイムアウト
   - タイムアウトを付与するには、BotにTimeout Members権限が必要です
