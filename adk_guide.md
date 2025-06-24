# Google Agent Development Kit (ADK) 完全ガイド

## 目次

1. [概要](#概要)
2. [環境構築・インストール](#環境構築インストール)
3. [認証設定](#認証設定)
4. [基本的なエージェント作成](#基本的なエージェント作成)
5. [ツールの実装](#ツールの実装)
6. [マルチエージェントシステム](#マルチエージェントシステム)
7. [MCPツール統合](#MCPツール統合)
8. [デプロイメント](#デプロイメント)
9. [セキュリティ・本番環境のベストプラクティス](#セキュリティ本番環境のベストプラクティス)
10. [トラブルシューティング](#トラブルシューティング)

---

## 概要

Google Agent Development Kit (ADK) は、AIエージェントの開発・評価・デプロイのためのオープンソースPythonツールキットです。

### 主な特徴

- **モデル非依存**: Gemini、Claude、Mistral AIなど様々なLLMをサポート
- **デプロイ非依存**: ローカル、Cloud Run、Kubernetes、Vertex AIなど様々な環境
- **フレームワーク互換**: LangChain、HuggingFace、Vertex AI、Firebaseとの統合
- **エンタープライズ対応**: Google Cloudのベストプラクティスに基づく設計

### システム要件

- Python 3.9+ (推奨: Python 3.10+)
- Java 17+ (Javaを使用する場合)
- ローカルIDE (VS Code、PyCharmなど)
- ターミナルアクセス

---

## 環境構築・インストール

### Python環境のセットアップ

1. **仮想環境の作成**
```bash
python -m venv .venv
```

2. **仮想環境の有効化**
```bash
# macOS/Linux
source .venv/bin/activate

# Windows CMD
.venv\Scripts\activate.bat

# Windows PowerShell
.venv\Scripts\Activate.ps1
```

3. **ADKのインストール**
```bash
# 安定版 (推奨)
pip install google-adk

# 開発版 (最新機能)
pip install git+https://github.com/google/adk-python.git@main
```

4. **インストール確認**
```bash
pip show google-adk
```

### Java環境のセットアップ

**Maven (`pom.xml`)**
```xml
<dependencies>
  <dependency>
    <groupId>com.google.adk</groupId>
    <artifactId>google-adk</artifactId>
    <version>0.1.0</version>
  </dependency>
  <dependency>
    <groupId>com.google.adk</groupId>
    <artifactId>google-adk-dev</artifactId>
    <version>0.1.0</version>
  </dependency>
</dependencies>
```

**Gradle (`build.gradle`)**
```gradle
dependencies {
  implementation 'com.google.adk:google-adk:0.1.0'
  implementation 'com.google.adk:google-adk-dev:0.1.0'
}
```

### プロジェクト構造

**Python**
```
multi_tool_agent/
├── __init__.py
├── agent.py
└── .env
```

**Java**
```
project_folder/
└── src/main/java/agents/multitool/
    └── MultiToolAgent.java
```

---

## 認証設定

### 認証方法の種類

ADKは以下の認証方法をサポートしています：

1. **Google AI Studio (API Key)**
2. **Google Cloud Vertex AI**
3. **OAuth2**
4. **OpenID Connect**
5. **Service Account**

### Google Cloud認証

1. **Google Cloud CLIのインストール**
```bash
# macOS
brew install google-cloud-sdk

# その他のプラットフォーム
# https://cloud.google.com/sdk/docs/install
```

2. **認証の実行**
```bash
gcloud auth application-default login
```

3. **環境変数の設定** (`.env`ファイル)
```bash
GOOGLE_CLOUD_PROJECT="your-project-id"
GOOGLE_CLOUD_LOCATION="us-central1"
GOOGLE_GENAI_USE_VERTEXAI="True"
```

### Google AI Studio認証

```bash
GOOGLE_API_KEY="your-api-key"
```

### 認証コンポーネント

**AuthScheme**: APIが期待する認証方法を定義
- `API_KEY`: シンプルなキー/値認証
- `OAUTH2`: 標準OAuth 2.0フロー
- `SERVICE_ACCOUNT`: Google Cloud Service Account

**AuthCredential**: 認証の初期情報を保持

---

## 基本的なエージェント作成

### シンプルなエージェント

```python
from google.adk.agents import Agent
from google.adk.tools import google_search

# 基本エージェント
root_agent = Agent(
    name="search_assistant",
    model="gemini-2.5-flash-preview-05-20",
    instruction="あなたは検索機能を持つアシスタントです。",
    description="Web検索ができるアシスタント",
    tools=[google_search]
)
```

### エージェントの種類

#### 1. LLMエージェント
```python
from google.adk.agents import Agent

llm_agent = Agent(
    model="gemini-2.5-flash-preview-05-20",
    name="LLMAgent",
    instruction="自然言語で様々なタスクを処理します。",
    tools=[google_search]
)
```

#### 2. ワークフローエージェント
```python
from google.adk.agents import SequentialAgent, ParallelAgent

# 順次実行
sequential_agent = SequentialAgent(
    sub_agents=[agent1, agent2, agent3]
)

# 並列実行
parallel_agent = ParallelAgent(
    sub_agents=[agent1, agent2, agent3]
)
```

#### 3. カスタムエージェント
```python
from google.adk.agents import BaseAgent

class CustomAgent(BaseAgent):
    def __init__(self, name: str):
        super().__init__(name=name)
    
    async def run_async(self, request, context):
        # カスタムロジックの実装
        return "カスタム処理の結果"
```

### エージェントの実行

```bash
# Web UI
adk web

# CLI
adk run agent_name

# API Server
adk api_server
```

---

## ツールの実装

### FunctionToolの作成

#### 基本的なFunctionTool
```python
from google.adk.tools import FunctionTool

def get_weather(location: str) -> dict:
    """指定された場所の天気情報を取得します。
    
    Args:
        location: 場所の名前
        
    Returns:
        天気情報の辞書
    """
    # 天気API呼び出しのロジック
    return {
        "location": location,
        "temperature": "22°C",
        "condition": "晴れ"
    }

# ツールとして登録
weather_tool = FunctionTool(func=get_weather)
```

#### 長時間実行ツール
```python
from google.adk.tools import LongRunningFunctionTool

def process_large_file(file_path: str, progress_callback=None) -> dict:
    """大きなファイルを処理します。
    
    Args:
        file_path: ファイルパス
        progress_callback: 進捗コールバック
        
    Returns:
        処理結果
    """
    # 長時間の処理
    for i in range(100):
        if progress_callback:
            progress_callback(f"処理中: {i}%")
        time.sleep(0.1)
    
    return {"status": "完了", "result": "処理結果"}

long_running_tool = LongRunningFunctionTool(func=process_large_file)
```

### 組み込みツール

#### 1. Google Search
```python
from google.adk.tools import google_search

agent = Agent(
    name="search_agent",
    model="gemini-2.5-flash-preview-05-20",
    tools=[google_search]
)
```

#### 2. Code Execution
```python
# Gemini 2モデルでのみ利用可能
agent = Agent(
    name="code_agent",
    model="gemini-2.5-flash-preview-05-20",
    built_in_tools=["code_execution"]
)
```

#### 3. Vertex AI Search
```python
from google.adk.tools import VertexAiSearchTool

vertex_search = VertexAiSearchTool(
    data_store_id="your-data-store-id"
)
```

### カスタムツールセット

```python
from google.adk.tools import BaseToolset, FunctionTool

class MathToolset(BaseToolset):
    def get_tools(self):
        return [
            FunctionTool(func=self.add_numbers),
            FunctionTool(func=self.subtract_numbers)
        ]
    
    def add_numbers(self, a: float, b: float) -> float:
        """2つの数値を足し算します。"""
        return a + b
    
    def subtract_numbers(self, a: float, b: float) -> float:
        """2つの数値を引き算します。"""
        return a - b

math_toolset = MathToolset()
```

### ツール使用時の制限事項

- **1エージェントあたり1つの組み込みツール**のみ
- **サブエージェントでは組み込みツール使用不可**
- **組み込みツールと他のツールの混在不可**

---

## マルチエージェントシステム

### 通信パターン

#### 1. 共有セッション状態
```python
# エージェント1が状態に書き込み
def agent1_task(context):
    context.state['data_key'] = "処理されたデータ"
    return "完了"

# エージェント2が状態から読み取り
def agent2_task(context):
    data = context.state.get('data_key')
    return f"受信したデータ: {data}"
```

#### 2. LLM駆動デリゲーション
```python
coordinator = Agent(
    name="coordinator",
    model="gemini-2.5-flash-preview-05-20",
    instruction="適切な専門エージェントにタスクを転送してください。",
    sub_agents={
        "tech_specialist": tech_agent,
        "business_specialist": business_agent
    }
)
```

#### 3. エージェント・ツール呼び出し
```python
from google.adk.tools import AgentTool

specialist_tool = AgentTool(agent=specialist_agent)

main_agent = Agent(
    name="main_agent",
    model="gemini-2.5-flash-preview-05-20",
    tools=[specialist_tool]
)
```

### 一般的なパターン

#### 1. コーディネーター/ディスパッチャー
```python
# 中央エージェントがリクエストを専門エージェントにルーティング
coordinator = Agent(
    name="coordinator",
    instruction="リクエストを適切な専門家に転送",
    sub_agents={
        "technical": tech_agent,
        "business": business_agent,
        "legal": legal_agent
    }
)
```

#### 2. 順次パイプライン
```python
pipeline = SequentialAgent(
    sub_agents=[
        validator_agent,    # 入力検証
        processor_agent,    # データ処理
        formatter_agent     # 結果整形
    ]
)
```

#### 3. 並列ファンアウト/収集
```python
parallel_processor = ParallelAgent(
    sub_agents=[
        analysis_agent1,
        analysis_agent2,
        analysis_agent3
    ]
)

# 結果収集エージェント
gatherer = Agent(
    name="gatherer",
    instruction="並列処理の結果をまとめてください"
)
```

#### 4. 階層タスク分解
```python
# 多階層エージェント構造
project_manager = Agent(
    name="project_manager",
    sub_agents={
        "development_team": dev_coordinator,
        "testing_team": test_coordinator,
        "deployment_team": deploy_coordinator
    }
)
```

#### 5. レビュー/批評パターン
```python
# 生成と批評の組み合わせ
generator = Agent(name="generator", instruction="コンテンツを生成")
critic = Agent(name="critic", instruction="品質をチェック")

review_system = SequentialAgent(
    sub_agents=[generator, critic]
)
```

### Agent-to-Agent (A2A) プロトコル

```python
# A2Aエンドポイントの設定
agent.expose_endpoint("/run")  # 標準エンドポイント
agent.create_agent_card()      # メタデータ公開

# 他のエージェントとの通信
response = await agent.call_external_agent(
    endpoint="http://other-agent:8000/run",
    message="タスクの依頼"
)
```

---

## MCPツール統合

Model Context Protocol (MCP) は、LLMアプリケーションと外部データソース・ツール間のシームレスな統合を可能にするオープンプロトコルです。ADKはMCPツールとの統合を標準でサポートしています。

### MCPツールセットの基本

#### MCPToolsetの設定

```python
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters, SseServerParams
from google.adk.agents import Agent

# ローカルMCPサーバー接続
local_mcp = MCPToolset(
    connection_params=StdioServerParameters(
        command='npx',
        args=["-y", "@modelcontextprotocol/server-filesystem", "./data"]
    ),
    tool_filter=['read_file', 'list_directory']  # オプション: 使用するツールを限定
)

# リモートMCPサーバー接続
remote_mcp = MCPToolset(
    connection_params=SseServerParams(
        url="https://my-mcp-server.example.com/sse",
        headers={"Authorization": "Bearer your-token"}
    )
)

# エージェントに統合
agent = Agent(
    name="mcp_agent",
    model="gemini-2.5-flash-preview-05-20",
    instruction="MCPツールを使用してタスクを実行してください。",
    tools=[local_mcp, remote_mcp]
)
```

### ブラウザ自動操作

#### 1. Microsoft Playwright MCP (公式)

```bash
# インストール
npx @playwright/mcp@latest

# Claude Desktop設定 (claude_desktop_config.json)
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    }
  }
}
```

**ADKでの使用例:**

```python
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

# Playwright MCPツールセット
playwright_mcp = MCPToolset(
    connection_params=StdioServerParameters(
        command='npx',
        args=["@playwright/mcp@latest"]
    ),
    tool_filter=['navigate', 'click', 'type', 'screenshot']
)

# ブラウザ自動操作エージェント
browser_agent = Agent(
    name="browser_automation",
    model="gemini-2.5-flash-preview-05-20",
    instruction="""
    あなたはWebブラウザを自動操作するアシスタントです。
    以下の機能を提供します：
    - Webページへのナビゲーション
    - 要素のクリック・入力
    - スクリーンショット取得
    - データ抽出
    """,
    tools=[playwright_mcp]
)
```

#### 2. ExecuteAutomation Playwright MCP

```bash
# インストール
npx @executeautomation/playwright-mcp-server

# より高度な機能
```

```python
# Web scraping example
playwright_advanced = MCPToolset(
    connection_params=StdioServerParameters(
        command='npx',
        args=["@executeautomation/playwright-mcp-server"]
    ),
    tool_filter=['navigate', 'extract_text', 'fill_form', 'wait_for_element']
)

scraper_agent = Agent(
    name="web_scraper",
    instruction="Webサイトから情報を抽出してください。",
    tools=[playwright_advanced]
)
```

#### 3. Puppeteer MCP (Python)

```python
# Python実装のPuppeteer MCPサーバー
puppeteer_mcp = MCPToolset(
    connection_params=StdioServerParameters(
        command='python',
        args=["/path/to/mcp-server-puppeteer-py/server.py"]
    )
)
```

### Google Services統合

#### 1. Google Calendar MCP

```bash
# インストール
npx @cocal/google-calendar-mcp

# または
git clone https://github.com/nspady/google-calendar-mcp
cd google-calendar-mcp
npm install
```

**ADKでの使用例:**

```python
# Google Calendar MCPツールセット
calendar_mcp = MCPToolset(
    connection_params=StdioServerParameters(
        command='npx',
        args=["-y", "@cocal/google-calendar-mcp"]
    ),
    tool_filter=['create_event', 'list_events', 'update_event', 'delete_event']
)

# カレンダー管理エージェント
calendar_agent = Agent(
    name="calendar_assistant",
    model="gemini-2.5-flash-preview-05-20",
    instruction="""
    あなたはGoogleカレンダーを管理するアシスタントです。
    以下の機能を提供します：
    - 予定の作成・更新・削除
    - 空き時間の確認
    - 会議のスケジューリング
    - 複数カレンダーの管理
    """,
    tools=[calendar_mcp]
)
```

**使用例:**

```python
# 会議スケジュール
response = calendar_agent.say("""
来週の火曜日10:00-11:00に「プロジェクト会議」を作成してください。
参加者: john@example.com, jane@example.com
場所: 会議室A
""")

# 空き時間確認
availability = calendar_agent.say("""
今週の私の空き時間を確認して、
1時間の会議に適した時間を3つ提案してください。
""")
```

#### 2. Gmail MCP

```bash
# Google Workspace MCP (Gmail + Calendar)
git clone https://github.com/epaproditus/google-workspace-mcp-server
cd google-workspace-mcp-server
npm install
```

```python
# Gmail MCPツールセット
gmail_mcp = MCPToolset(
    connection_params=StdioServerParameters(
        command='node',
        args=["/path/to/google-workspace-server/build/index.js"]
    ),
    tool_filter=['list_emails', 'send_email', 'search_emails', 'modify_email']
)

# メール管理エージェント
email_agent = Agent(
    name="email_assistant",
    model="gemini-2.5-flash-preview-05-20",
    instruction="""
    あなたはGmailを管理するアシスタントです。
    以下の機能を提供します：
    - メールの検索・リスト表示
    - メール送信
    - ラベル管理
    - メールの整理
    """,
    tools=[gmail_mcp]
)
```

**使用例:**

```python
# メール送信
email_agent.say("""
件名「会議資料について」で、
john@example.com に以下のメールを送信してください：

こんにちは、
明日の会議資料を添付いたします。
ご確認ください。
""")

# メール検索
email_agent.say("""
過去1週間の未読メールから、
「緊急」または「重要」を含むメールを検索してください。
""")
```

#### 3. Google Drive MCP

```python
# Google Drive MCPツールセット
drive_mcp = MCPToolset(
    connection_params=StdioServerParameters(
        command='npx',
        args=["-y", "@your-org/google-drive-mcp"]
    ),
    tool_filter=['list_files', 'upload_file', 'download_file', 'share_file']
)

# ファイル管理エージェント
drive_agent = Agent(
    name="drive_assistant",
    instruction="Google Driveのファイル管理を行います。",
    tools=[drive_mcp]
)
```

### 高度なMCP統合パターン

#### 1. マルチサービス統合

```python
# 複数のGoogleサービスを統合
multi_service_agent = Agent(
    name="google_suite_assistant",
    model="gemini-2.5-flash-preview-05-20",
    instruction="""
    あなたはGoogle Workspace全体を管理するアシスタントです。
    カレンダー、Gmail、Driveを連携して作業を効率化します。
    """,
    tools=[calendar_mcp, gmail_mcp, drive_mcp]
)

# 統合タスク例
response = multi_service_agent.say("""
明日の会議「プロジェクト進捗報告」について：
1. 会議資料をDriveから検索
2. 参加者にメールで資料を共有
3. カレンダーに資料リンクを追加
""")
```

#### 2. ブラウザ + Google Services

```python
# ブラウザ自動操作 + Google Services
automation_agent = Agent(
    name="web_automation_assistant",
    model="gemini-2.5-flash-preview-05-20",
    instruction="""
    WebブラウザとGoogleサービスを連携して、
    情報収集から報告まで自動化します。
    """,
    tools=[playwright_mcp, calendar_mcp, gmail_mcp]
)

# 自動レポート作成
automation_agent.say("""
競合他社のWebサイトから価格情報を収集し、
結果をスプレッドシートにまとめて、
関係者にメールで共有してください。
""")
```

#### 3. カスタムMCPサーバー作成

```python
# カスタムMCPサーバーの実装例
import asyncio
from mcp import Server
from mcp.tools import Tool

server = Server("custom-service")

@server.tool()
async def custom_api_call(endpoint: str, params: dict) -> dict:
    """カスタムAPI呼び出し"""
    # API呼び出しロジック
    return {"result": "success"}

@server.tool()
async def data_processing(data: list) -> dict:
    """データ処理"""
    # データ処理ロジック
    return {"processed": len(data)}

# ADKでの使用
custom_mcp = MCPToolset(
    connection_params=StdioServerParameters(
        command='python',
        args=["custom_mcp_server.py"]
    )
)
```

### MCPツール認証設定

#### Google Services認証

```bash
# Google Cloud プロジェクト設定
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_CLIENT_ID="your-oauth-client-id"
export GOOGLE_CLIENT_SECRET="your-oauth-client-secret"

# OAuth2スコープ設定
GOOGLE_CALENDAR_SCOPES="https://www.googleapis.com/auth/calendar"
GOOGLE_GMAIL_SCOPES="https://www.googleapis.com/auth/gmail.modify"
GOOGLE_DRIVE_SCOPES="https://www.googleapis.com/auth/drive"
```

#### ブラウザ自動操作設定

```python
# Playwright設定
playwright_config = {
    "headless": True,  # ヘッドレスモード
    "viewport": {"width": 1920, "height": 1080},
    "user_agent": "ADK Browser Agent 1.0"
}
```

### MCPツールのベストプラクティス

#### 1. エラーハンドリング

```python
from google.adk.core import ToolCallback

class MCPToolCallback(ToolCallback):
    def on_tool_error(self, tool_name: str, error: Exception):
        if "connection" in str(error).lower():
            return "MCPサーバーへの接続に問題があります。再試行してください。"
        return f"ツールエラー: {str(error)}"

mcp_agent = Agent(
    name="robust_mcp_agent",
    tools=[calendar_mcp],
    callbacks=[MCPToolCallback()]
)
```

#### 2. パフォーマンス最適化

```python
# ツールフィルタリングでパフォーマンス向上
optimized_mcp = MCPToolset(
    connection_params=StdioServerParameters(
        command='npx',
        args=["@playwright/mcp@latest"]
    ),
    tool_filter=['navigate', 'click'],  # 必要なツールのみ
    cache_tools=True  # ツール情報をキャッシュ
)
```

#### 3. セキュリティ考慮事項

```python
# セキュアなMCP設定
secure_mcp = MCPToolset(
    connection_params=SseServerParams(
        url="https://secure-mcp-server.example.com/sse",
        headers={
            "Authorization": "Bearer your-secure-token",
            "X-API-Version": "v1"
        }
    ),
    timeout=30,  # タイムアウト設定
    max_retries=3  # リトライ回数制限
)
```

---

## デプロイメント

### ローカル開発

```bash
# Web UI
adk web

# CLI実行
adk run my_agent

# API Server
adk api_server
```

### Cloud Run デプロイ

#### 環境変数設定
```bash
export GOOGLE_CLOUD_PROJECT=your-project-id
export GOOGLE_CLOUD_LOCATION=us-central1
export GOOGLE_GENAI_USE_VERTEXAI=True
```

#### デプロイコマンド
```bash
# Python (推奨)
adk deploy cloud_run \
--project=$GOOGLE_CLOUD_PROJECT \
--region=$GOOGLE_CLOUD_LOCATION \
--service_name=my-agent-service \
--with_ui \
$AGENT_PATH

# gcloudコマンド (代替)
gcloud run deploy my-agent \
--source . \
--region us-central1 \
--allow-unauthenticated
```

### Google Kubernetes Engine (GKE)

#### Dockerfileの作成
```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["adk", "api_server"]
```

#### Kubernetesマニフェスト
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: adk-agent
spec:
  replicas: 3
  selector:
    matchLabels:
      app: adk-agent
  template:
    metadata:
      labels:
        app: adk-agent
    spec:
      containers:
      - name: agent
        image: gcr.io/PROJECT_ID/adk-agent:latest
        ports:
        - containerPort: 8000
        env:
        - name: GOOGLE_CLOUD_PROJECT
          value: "your-project-id"
---
apiVersion: v1
kind: Service
metadata:
  name: adk-agent-service
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8000
  selector:
    app: adk-agent
```

### Vertex AI Agent Engine

```python
# エージェントのVertex AI登録
from google.adk.deploy import vertex_ai_deploy

vertex_ai_deploy(
    agent=root_agent,
    project_id="your-project-id",
    location="us-central1",
    display_name="Production Agent"
)
```

### デプロイメント要件

- **エージェント構造**: `agent.py`または`CapitalAgent.java`
- **ルートエージェント**: `root_agent`の定義
- **初期化ファイル**: エージェントディレクトリに`__init__.py`

---

## セキュリティ・本番環境のベストプラクティス

### 認証セキュリティ

#### 1. 資格情報管理
```python
# 環境変数の使用
import os
api_key = os.getenv('GOOGLE_API_KEY')

# Google Cloud Secret Managerの使用
from google.cloud import secretmanager

def get_secret(secret_id):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{PROJECT_ID}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")
```

#### 2. OAuth2実装
```python
from google.adk.tools import AuthScheme, AuthCredential

oauth_scheme = AuthScheme(
    type="OAUTH2",
    client_id="your-client-id",
    client_secret="your-client-secret",
    scopes=["scope1", "scope2"]
)

oauth_credential = AuthCredential(
    scheme=oauth_scheme,
    redirect_uri="your-redirect-uri"
)
```

### セッション管理

#### 1. 本番環境のセッションサービス
```python
from google.adk.core import SessionService
import sqlite3
import json

class DatabaseSessionService(SessionService):
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
    
    async def get_session(self, session_id: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(
            "SELECT data FROM sessions WHERE session_id = ?", 
            (session_id,)
        )
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return json.loads(result[0])
        return {}
    
    async def save_session(self, session_id: str, data: dict):
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "INSERT OR REPLACE INTO sessions (session_id, data) VALUES (?, ?)",
            (session_id, json.dumps(data))
        )
        conn.commit()
        conn.close()
```

#### 2. 暗号化セッションストレージ
```python
from cryptography.fernet import Fernet
import base64

class EncryptedSessionService(SessionService):
    def __init__(self, encryption_key: bytes):
        self.cipher = Fernet(encryption_key)
    
    def encrypt_data(self, data: dict) -> str:
        json_data = json.dumps(data).encode()
        encrypted_data = self.cipher.encrypt(json_data)
        return base64.b64encode(encrypted_data).decode()
    
    def decrypt_data(self, encrypted_data: str) -> dict:
        encrypted_bytes = base64.b64decode(encrypted_data.encode())
        decrypted_data = self.cipher.decrypt(encrypted_bytes)
        return json.loads(decrypted_data.decode())
```

### セキュリティガードレール

#### 1. 入力検証
```python
from google.adk.core import ModelCallback

class SecurityCallback(ModelCallback):
    def __init__(self):
        self.banned_words = ["機密", "パスワード", "秘密"]
    
    def on_llm_request(self, request):
        # 入力フィルタリング
        for word in self.banned_words:
            if word in request.message:
                raise ValueError(f"禁止されたキーワード: {word}")
        return request
    
    def on_llm_response(self, response):
        # 出力フィルタリング
        for word in self.banned_words:
            if word in response.content:
                response.content = response.content.replace(word, "[削除済み]")
        return response

# エージェントに適用
agent = Agent(
    name="secure_agent",
    model="gemini-2.5-flash-preview-05-20",
    callbacks=[SecurityCallback()]
)
```

#### 2. ツール実行制限
```python
from google.adk.tools import ToolContext

def secure_database_query(query: str, tool_context: ToolContext) -> dict:
    """セキュアなデータベースクエリ実行"""
    
    # ユーザー認証確認
    if not tool_context.user_id:
        raise ValueError("認証が必要です")
    
    # クエリ検証
    forbidden_keywords = ["DROP", "DELETE", "UPDATE", "INSERT"]
    if any(keyword in query.upper() for keyword in forbidden_keywords):
        raise ValueError("危険なクエリは実行できません")
    
    # 読み取り専用クエリのみ実行
    if not query.strip().upper().startswith("SELECT"):
        raise ValueError("SELECT文のみ許可されています")
    
    # クエリ実行
    return execute_read_only_query(query)
```

### ネットワークセキュリティ

#### 1. VPC設定
```python
# Cloud Run環境変数
environment_variables = {
    "VPC_CONNECTOR": "projects/PROJECT_ID/locations/REGION/connectors/CONNECTOR_NAME",
    "EGRESS_SETTINGS": "private-ranges-only"
}
```

#### 2. ファイアウォール規則
```bash
# エージェント間通信の制限
gcloud compute firewall-rules create allow-agent-communication \
--allow tcp:8000 \
--source-ranges 10.0.0.0/8 \
--target-tags adk-agent
```

### コード実行のセキュリティ

#### 1. サンドボックス環境
```python
import subprocess
import tempfile
import os

def execute_code_safely(code: str) -> str:
    """コードを安全な環境で実行"""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # ネットワークアクセスなしで実行
        result = subprocess.run(
            ["python", "-c", code],
            cwd=temp_dir,
            capture_output=True,
            text=True,
            timeout=30,  # タイムアウト設定
            env={"PATH": "/usr/bin:/bin"}  # 最小限の環境
        )
        
        return result.stdout
```

### 監査とロギング

#### 1. 構造化ログ
```python
import structlog
from google.adk.core import ModelCallback

class AuditCallback(ModelCallback):
    def __init__(self):
        self.logger = structlog.get_logger()
    
    def on_llm_request(self, request):
        self.logger.info(
            "llm_request",
            user_id=request.context.user_id,
            agent_name=request.agent_name,
            message_length=len(request.message)
        )
        return request
    
    def on_tool_call(self, tool_call):
        self.logger.info(
            "tool_execution",
            tool_name=tool_call.name,
            user_id=tool_call.context.user_id,
            parameters=tool_call.parameters
        )
        return tool_call
```

#### 2. セキュリティメトリクス
```python
from prometheus_client import Counter, Histogram

# メトリクス定義
security_events = Counter('security_events_total', 'セキュリティイベント', ['event_type'])
response_time = Histogram('agent_response_time_seconds', 'エージェント応答時間')

# 使用例
def secure_agent_call(request):
    with response_time.time():
        try:
            return agent.run(request)
        except SecurityException as e:
            security_events.labels(event_type='security_violation').inc()
            raise
```

---

## トラブルシューティング

### よくある問題と解決方法

#### 1. インポートエラー
```bash
# エラー: cannot import name 'Tool' from 'google.adk.tools'
# 解決方法: 正しいクラス名を使用
from google.adk.tools import FunctionTool  # ✓ 正しい
from google.adk.tools import Tool          # ✗ 存在しない
```

#### 2. 複数ツールエラー
```bash
# エラー: Multiple tools are supported only when they are all search tools
# 解決方法: 組み込みツールと他のツールを分離
```

```python
# ✗ 混在不可
agent = Agent(
    tools=[google_search, custom_tool]  # エラー
)

# ✓ 分離
search_agent = Agent(tools=[google_search])
custom_agent = Agent(tools=[custom_tool])
```

#### 3. 認証エラー
```bash
# エラー: Authentication failed
# 確認事項:
gcloud auth list                    # 認証状態確認
gcloud config get-value project    # プロジェクト確認
gcloud auth application-default login  # 再認証
```

#### 4. モジュール循環参照
```python
# 解決方法: 絶対パスでインポート
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from module_name import tool
```

#### 5. メモリ不足
```python
# 解決方法: ストリーミング処理
def process_large_data(data_stream):
    for chunk in data_stream:
        yield process_chunk(chunk)
```

### デバッグ技法

#### 1. ログレベル設定
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# ADK専用ログ
adk_logger = logging.getLogger('google.adk')
adk_logger.setLevel(logging.DEBUG)
```

#### 2. トレーシング
```python
from google.adk.core import TraceCallback

class DebugCallback(TraceCallback):
    def on_agent_start(self, agent_name):
        print(f"エージェント開始: {agent_name}")
    
    def on_tool_call(self, tool_name, parameters):
        print(f"ツール呼び出し: {tool_name}, {parameters}")
    
    def on_agent_end(self, agent_name, result):
        print(f"エージェント終了: {agent_name}, 結果: {result}")
```

#### 3. パフォーマンス監視
```python
import time
from functools import wraps

def performance_monitor(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__}: {end_time - start_time:.2f}秒")
        return result
    return wrapper

@performance_monitor
def my_tool_function(data):
    # ツールの処理
    return processed_data
```

### エラー処理のベストプラクティス

#### 1. 適切な例外処理
```python
from google.adk.core import AgentException

def robust_agent_call(agent, message):
    try:
        return agent.say(message)
    except AgentException as e:
        logger.error(f"エージェントエラー: {e}")
        return "申し訳ございません。処理中にエラーが発生しました。"
    except Exception as e:
        logger.critical(f"予期しないエラー: {e}")
        return "システムエラーが発生しました。管理者にお問い合わせください。"
```

#### 2. 段階的フォールバック
```python
def resilient_search(query):
    try:
        # 1次: 専門検索
        return specialized_search(query)
    except SpecializedSearchError:
        try:
            # 2次: 一般検索
            return general_search(query)
        except GeneralSearchError:
            # 3次: 静的応答
            return "申し訳ございません。検索機能が利用できません。"
```

### 本番環境での監視

#### 1. ヘルスチェック
```python
from fastapi import FastAPI
from google.adk.core import AgentStatus

app = FastAPI()

@app.get("/health")
def health_check():
    try:
        # エージェントの状態確認
        status = agent.get_status()
        if status == AgentStatus.READY:
            return {"status": "healthy"}
        else:
            return {"status": "unhealthy", "reason": "Agent not ready"}
    except Exception as e:
        return {"status": "unhealthy", "reason": str(e)}
```

#### 2. メトリクス収集
```python
from prometheus_client import Counter, Histogram, start_http_server

# メトリクス定義
request_count = Counter('agent_requests_total', 'Total requests')
request_duration = Histogram('agent_request_duration_seconds', 'Request duration')
error_count = Counter('agent_errors_total', 'Total errors', ['error_type'])

# メトリクス露出
start_http_server(8080)  # Prometheusエンドポイント
```

---

## まとめ

Google ADKは強力で柔軟なAIエージェント開発フレームワークです。本ガイドでは、基本的なセットアップから高度なマルチエージェントシステム、本番環境でのセキュリティ考慮事項まで網羅的に説明しました。

### 重要なポイント

1. **段階的開発**: 単純なエージェントから始めて、徐々に複雑な機能を追加
2. **セキュリティ重視**: 認証、承認、監査を初期段階から考慮
3. **テスト駆動**: 開発環境での十分なテストから本番デプロイへ
4. **監視とロギング**: 運用開始後の継続的な監視体制の構築
5. **スケーラビリティ**: 将来の拡張を見据えたアーキテクチャ設計

### 追加リソース

- [公式ドキュメント](https://google.github.io/adk-docs/)
- [GitHub リポジトリ](https://github.com/google/adk-python)
- [サンプル集](https://github.com/google/adk-samples)
- [Google Cloud Codelabs](https://codelabs.developers.google.com/)

このガイドが、Google ADKを使用したAIエージェント開発の成功に役立つことを願っています。