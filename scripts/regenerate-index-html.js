#!/usr/bin/env node

/**
 * index.html完全再生成スクリプト
 * 既存ファイルを壊さずに、テンプレートから新しく作成
 */

const fs = require('fs');
const path = require('path');

// 完全なHTMLテンプレート
const HTML_TEMPLATE = `<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GenieUs Documentation</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: #cccccc;
            background-color: #1e1e1e;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            background: linear-gradient(135deg, #0e4f79 0%, #2d5a87 100%);
            color: white;
            padding: 40px 20px;
            text-align: center;
            border-radius: 12px;
            margin-bottom: 40px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            border: 1px solid #30363d;
        }
        
        .header h1 {
            font-size: 3rem;
            margin-bottom: 10px;
            font-weight: 700;
        }
        
        .header p {
            font-size: 1.2rem;
            opacity: 0.9;
        }
        
        .nav-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        
        .nav-card {
            background: #252526;
            border: 1px solid #30363d;
            border-radius: 12px;
            padding: 24px;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        }
        
        .nav-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.4);
            border-color: #569cd6;
        }
        
        .nav-card h3 {
            color: #569cd6;
            margin-bottom: 16px;
            font-size: 1.5rem;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .nav-card ul {
            list-style: none;
        }
        
        .nav-card li {
            margin-bottom: 8px;
        }
        
        .nav-card a {
            color: #9cdcfe;
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 12px;
            border-radius: 6px;
            transition: background-color 0.2s ease;
        }
        
        .nav-card a:hover {
            background-color: #2a2d2e;
            color: #ffffff;
            text-decoration: none;
        }
        
        .quick-start {
            background: linear-gradient(135deg, #0e4f79 0%, #2d5a87 100%);
            color: white;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 30px;
            border: 1px solid #30363d;
        }
        
        .quick-start h2 {
            margin-bottom: 20px;
            font-size: 1.8rem;
        }
        
        .quick-links {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }
        
        .quick-link {
            background: rgba(255, 255, 255, 0.1);
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            transition: all 0.2s ease;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .quick-link:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: scale(1.02);
            border-color: rgba(255, 255, 255, 0.3);
        }
        
        .quick-link a {
            color: white;
            text-decoration: none;
            font-weight: 500;
        }
        
        .footer {
            text-align: center;
            padding: 30px;
            color: #858585;
            border-top: 1px solid #30363d;
            margin-top: 40px;
        }
        
        .emoji {
            font-size: 1.2em;
        }
        
        .badge {
            display: inline-block;
            background: #21262d;
            border: 1px solid #30363d;
            border-radius: 20px;
            padding: 4px 12px;
            font-size: 0.875rem;
            color: #858585;
            margin-left: 8px;
        }
        
        @media (max-width: 768px) {
            .header h1 {
                font-size: 2rem;
            }
            
            .nav-grid {
                grid-template-columns: 1fr;
            }
            
            .quick-links {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><span class="emoji">🧞‍♂️</span> GenieUs Documentation</h1>
            <p>見えない成長に、光をあてる。不安な毎日を、自信に変える。</p>
        </div>
        
        <div class="quick-start">
            <h2><span class="emoji">🚀</span> すぐ始める</h2>
            <div class="quick-links">
                <div class="quick-link">
                    <a href="development/quick-start.md">環境構築・起動</a>
                </div>
                <div class="quick-link">
                    <a href="development/coding-standards.md">コーディング規約</a>
                </div>
                <div class="quick-link">
                    <a href="architecture/overview.md">アーキテクチャ概要</a>
                </div>
            </div>
        </div>
        
        <!--NAV_GRID_PLACEHOLDER-->
        
        <div class="footer">
            <p>📖 GenieUs Documentation - AI子育て支援プラットフォーム</p>
            <p>🤖 自動更新対応Webビューアー - Generated with Claude Code<!--TIMESTAMP_PLACEHOLDER--></p>
            <p style="margin-top: 10px; font-size: 0.8rem; color: #666;">
                💡 高機能ビューアー: <a href="web/index.html" style="color: #9cdcfe;">docs/web/index.html</a>
            </p>
        </div>
    </div>
    
    <script>
        // MarkdownリンクをHTMLで表示する際の処理
        document.addEventListener('DOMContentLoaded', function() {
            const links = document.querySelectorAll('a[href$=".md"]');
            
            links.forEach(link => {
                link.addEventListener('click', function(e) {
                    e.preventDefault();
                    const href = this.getAttribute('href');
                    
                    // Markdownファイルの内容を取得して表示
                    fetch(href)
                        .then(response => response.text())
                        .then(markdown => {
                            // 簡単なMarkdown to HTMLコンバーター
                            showMarkdownContent(markdown, href);
                        })
                        .catch(error => {
                            console.error('Error loading markdown:', error);
                            // フォールバック: 新しいタブで開く
                            window.open(href, '_blank');
                        });
                });
            });
        });
        
        function showMarkdownContent(markdown, title) {
            // シンプルなMarkdown表示モーダル
            const modal = document.createElement('div');
            modal.style.cssText = \`
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0,0,0,0.8);
                z-index: 1000;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            \`;
            
            const content = document.createElement('div');
            content.style.cssText = \`
                background: white;
                border-radius: 12px;
                padding: 30px;
                max-width: 800px;
                max-height: 80vh;
                overflow-y: auto;
                position: relative;
            \`;
            
            const closeBtn = document.createElement('button');
            closeBtn.innerHTML = '✕';
            closeBtn.style.cssText = \`
                position: absolute;
                top: 15px;
                right: 15px;
                background: none;
                border: none;
                font-size: 20px;
                cursor: pointer;
                color: #666;
            \`;
            
            closeBtn.onclick = () => modal.remove();
            
            // 簡単なMarkdown to HTML変換
            const html = markdown
                .replace(/^# (.*$)/gim, '<h1>$1</h1>')
                .replace(/^## (.*$)/gim, '<h2>$1</h2>')
                .replace(/^### (.*$)/gim, '<h3>$1</h3>')
                .replace(/\\*\\*(.*?)\\*\\*/gim, '<strong>$1</strong>')
                .replace(/\\*(.*?)\\*/gim, '<em>$1</em>')
                .replace(/\\n/gim, '<br>');
            
            content.innerHTML = \`
                <h2 style="margin-bottom: 20px; color: #667eea;">\${title}</h2>
                <div style="line-height: 1.6;">\${html}</div>
            \`;
            
            content.appendChild(closeBtn);
            modal.appendChild(content);
            document.body.appendChild(modal);
            
            modal.onclick = (e) => {
                if (e.target === modal) modal.remove();
            };
        }
    </script>
</body>
</html>`;

// navigation.jsonを読み込んでHTML生成する関数
function generateFromNavigationJson() {
    const navJsonPath = path.join(__dirname, '..', 'docs', 'web', 'config', 'navigation.json');
    const indexPath = path.join(__dirname, '..', 'docs', 'index.html');
    
    try {
        const navData = JSON.parse(fs.readFileSync(navJsonPath, 'utf-8'));
        let navGridHtml = '<div class="nav-grid">\n';
        
        // quickstartセクションをスキップ（別途表示済み）
        const filteredSections = navData.sections.filter(section => section.id !== 'quickstart');
        
        for (const section of filteredSections) {
            if (!section.items || section.items.length === 0) continue;
            
            const emojiMatch = section.title.match(/^([^\s]+)/);
            const emoji = emojiMatch ? emojiMatch[1] : '📄';
            const titleWithoutEmoji = section.title.replace(/^[^\s]+\s*/, '');
            
            navGridHtml += `            <div class="nav-card">\n`;
            navGridHtml += `                <h3><span class="emoji">${emoji}</span> ${titleWithoutEmoji}</h3>\n`;
            navGridHtml += `                <ul>\n`;
            
            for (const item of section.items) {
                navGridHtml += `                    <li><a href="${item.file}">${item.title}</a></li>\n`;
            }
            
            navGridHtml += `                </ul>\n`;
            navGridHtml += `            </div>\n`;
            navGridHtml += `            \n`;
        }
        
        navGridHtml += '        </div>';
        
        // タイムスタンプ生成
        const timestamp = new Date().toLocaleString('ja-JP');
        
        // テンプレートの置換
        let html = HTML_TEMPLATE;
        html = html.replace('<!--NAV_GRID_PLACEHOLDER-->', navGridHtml);
        html = html.replace('<!--TIMESTAMP_PLACEHOLDER-->', ` - 最終更新: ${timestamp}`);
        
        // ファイル書き込み
        fs.writeFileSync(indexPath, html, 'utf-8');
        console.log(`✅ index.html を完全再生成しました (${filteredSections.length}セクション)`);
        
    } catch (error) {
        console.error('❌ エラー:', error.message);
        process.exit(1);
    }
}

// 直接実行時
if (require.main === module) {
    generateFromNavigationJson();
}

module.exports = { generateFromNavigationJson };