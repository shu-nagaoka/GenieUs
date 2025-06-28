#!/usr/bin/env python3
"""
GenieUs Documentation Server

Markdownドキュメントをローカルで閲覧するためのシンプルHTTPサーバー
"""

import http.server
import socketserver
import webbrowser
import os
import sys
from pathlib import Path


class DocumentationHandler(http.server.SimpleHTTPRequestHandler):
    """ドキュメント専用のHTTPハンドラー"""

    def end_headers(self):
        # CORS対応（ローカル開発用）
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_GET(self):
        """GETリクエストハンドリング"""
        # ルートアクセス時は新しいweb/index.htmlにリダイレクト
        if self.path == "/":
            self.path = "/web/index.html"

        # .mdファイルに適切なContent-Typeを設定
        if self.path.endswith(".md"):
            self.send_response(200)
            self.send_header("Content-type", "text/plain; charset=utf-8")
            self.end_headers()

            try:
                with open(self.path[1:], "r", encoding="utf-8") as f:
                    self.wfile.write(f.read().encode("utf-8"))
            except FileNotFoundError:
                self.send_error(404, f"File not found: {self.path}")
            return

        # その他のファイルは標準処理
        super().do_GET()


def main():
    """メイン実行関数"""
    # docsディレクトリに移動
    docs_dir = Path(__file__).parent
    os.chdir(docs_dir)

    # ポート設定（レアケースなポート）
    PORT = 15080

    # ポート15080を使用しているプロセスを停止
    import subprocess

    try:
        result = subprocess.run(
            ["lsof", "-ti", f":{PORT}"], capture_output=True, text=True, check=False
        )
        if result.stdout.strip():
            pids = result.stdout.strip().split("\n")
            for pid in pids:
                if pid:
                    print(f"⚠️  ポート {PORT} が使用中です (PID: {pid})。停止中...")
                    subprocess.run(["kill", pid], check=False)
            import time

            time.sleep(2)
    except Exception as e:
        print(f"ポートチェック中にエラー: {e}")

    # サーバー起動の試行
    for port in range(PORT, PORT + 10):
        try:
            with socketserver.TCPServer(("", port), DocumentationHandler) as httpd:
                print(f"""
🧞‍♂️ GenieUs Documentation Server が起動しました！

📖 ドキュメントサイト: http://localhost:{port}
📋 レガシー版:       http://localhost:{port}/index.html
🎯 高機能版（推奨）:  http://localhost:{port}/web/index.html

💡 使い方:
  - ブラウザで上記URLにアクセス
  - 左サイドバーから読みたいドキュメントを選択
  - マークダウンが自動更新で綺麗にHTMLで表示されます
  
🔄 特徴:
  - マークダウンファイル自動更新検知（5秒間隔）
  - リアルタイム検索機能
  - レスポンシブデザイン

⏹️  停止: Ctrl+C
""")

                # ブラウザを自動で開く
                try:
                    webbrowser.open(f"http://localhost:{port}/web/index.html")
                except:
                    print("💡 ブラウザを手動で開いてください")

                # サーバー開始
                httpd.serve_forever()

        except OSError as e:
            if "Address already in use" in str(e):
                print(f"ポート {port} は使用中です。次のポートを試行...")
                continue
            else:
                print(f"❌ サーバー起動エラー: {e}")
                sys.exit(1)

    print("❌ 利用可能なポートが見つかりませんでした")
    sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 GenieUs Documentation Server を停止しました")
        sys.exit(0)
