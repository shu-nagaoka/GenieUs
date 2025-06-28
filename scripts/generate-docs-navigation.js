#!/usr/bin/env node

/**
 * ドキュメント自動更新スクリプト
 * - docs/ ディレクトリをスキャン
 * - navigation.json と index.html を自動生成
 * - ファイル監視モード対応
 */

const fs = require('fs');
const path = require('path');

class DocsNavigationGenerator {
    constructor() {
        this.docsDir = path.join(__dirname, '..', 'docs');
        this.webConfigDir = path.join(this.docsDir, 'web', 'config');
        this.navigationFile = path.join(this.webConfigDir, 'navigation.json');
        this.indexFile = path.join(this.docsDir, 'index.html');
        
        // カテゴリ設定（表示順序とアイコン）
        this.categoryConfig = {
            'quickstart': { title: '🚀 すぐ始める', order: 1 },
            'architecture': { title: '🏗️ アーキテクチャ', order: 2 },
            'development': { title: '👨‍💻 開発ガイド', order: 3 },
            'technical': { title: '⚙️ 技術詳細', order: 4 },
            'guides': { title: '📖 実装ガイド', order: 5 },
            'deployment': { title: '🚀 デプロイメント', order: 6 },
            'plan': { title: '📋 実装プラン', order: 7 },
            'issue': { title: '🎫 Issue管理', order: 8 },
            'blog': { title: '📝 ブログ', order: 9 }
        };
        
        // ファイル優先度設定
        this.filePriority = {
            // クイックスタート
            'development/quick-start.md': { category: 'quickstart', title: '⚡ クイックスタート', order: 1 },
            'development/coding-standards.md': { category: 'quickstart', title: '📝 コーディング規約', order: 2 },
            'architecture/overview.md': { category: 'quickstart', title: '🏗️ アーキテクチャ概要', order: 3 },
            
            // 特別扱いファイル
            'README.md': { ignore: true }, // ルートのREADMEは除外
        };
    }
    
    /**
     * メイン実行関数
     */
    async generate() {
        console.log('🔍 ドキュメント構造をスキャン中...');
        
        try {
            const docStructure = await this.scanDocsDirectory();
            console.log(`📁 ${Object.keys(docStructure).length}カテゴリ、${this.countTotalFiles(docStructure)}ファイルを検出`);
            
            await this.generateNavigationJson(docStructure);
            await this.generateIndexHtml();
            
            console.log('✅ ドキュメント自動更新完了');
            
        } catch (error) {
            console.error('❌ エラーが発生しました:', error);
            process.exit(1);
        }
    }
    
    /**
     * docsディレクトリをスキャンして構造を取得
     */
    async scanDocsDirectory() {
        const structure = {};
        
        const categories = fs.readdirSync(this.docsDir, { withFileTypes: true })
            .filter(dirent => dirent.isDirectory() && dirent.name !== 'web')
            .map(dirent => dirent.name);
        
        for (const category of categories) {
            const categoryPath = path.join(this.docsDir, category);
            const files = await this.scanCategory(categoryPath, category);
            
            if (files.length > 0) {
                structure[category] = files;
            }
        }
        
        // ルートディレクトリのMarkdownファイルもチェック
        const rootFiles = await this.scanCategory(this.docsDir, 'root', true);
        if (rootFiles.length > 0) {
            structure['root'] = rootFiles;
        }
        
        return structure;
    }
    
    /**
     * カテゴリディレクトリをスキャン
     */
    async scanCategory(categoryPath, categoryName, isRoot = false) {
        const files = [];
        
        try {
            const items = fs.readdirSync(categoryPath, { withFileTypes: true });
            
            for (const item of items) {
                if (item.isFile() && item.name.endsWith('.md')) {
                    // ルートの場合はディレクトリを除外
                    if (isRoot && this.isDirectoryName(item.name)) continue;
                    
                    const filePath = isRoot ? item.name : `${categoryName}/${item.name}`;
                    const fullPath = path.join(categoryPath, item.name);
                    
                    // 除外設定をチェック
                    if (this.filePriority[filePath]?.ignore) continue;
                    
                    const fileInfo = await this.analyzeMarkdownFile(fullPath, filePath);
                    if (fileInfo) {
                        files.push(fileInfo);
                    }
                }
            }
        } catch (error) {
            console.warn(`⚠️ カテゴリ ${categoryName} の読み込みに失敗: ${error.message}`);
        }
        
        // ファイルをソート（優先度 → アルファベット順）
        return files.sort((a, b) => {
            const orderA = a.order || 999;
            const orderB = b.order || 999;
            if (orderA !== orderB) return orderA - orderB;
            return a.title.localeCompare(b.title);
        });
    }
    
    /**
     * Markdownファイルを解析してメタデータ取得
     */
    async analyzeMarkdownFile(fullPath, relativePath) {
        try {
            const content = fs.readFileSync(fullPath, 'utf-8');
            const lines = content.split('\n');
            
            // タイトルを取得（最初の# ヘッダー）
            let title = this.extractTitle(lines, relativePath);
            let description = this.extractDescription(lines);
            
            // 優先度設定があればそれを使用
            const priority = this.filePriority[relativePath];
            if (priority) {
                title = priority.title || title;
                description = priority.description || description;
            }
            
            return {
                title,
                file: relativePath,
                description,
                order: priority?.order,
                lastModified: fs.statSync(fullPath).mtime
            };
            
        } catch (error) {
            console.warn(`⚠️ ファイル解析失敗: ${relativePath} - ${error.message}`);
            return null;
        }
    }
    
    /**
     * ファイルからタイトルを抽出
     */
    extractTitle(lines, relativePath) {
        // 最初の# ヘッダーを探す
        for (const line of lines) {
            const match = line.match(/^#\s+(.+)$/);
            if (match) {
                return this.addEmojiIfNeeded(match[1].trim());
            }
        }
        
        // ヘッダーがない場合はファイル名から生成
        const fileName = path.basename(relativePath, '.md');
        return this.addEmojiIfNeeded(this.formatFileName(fileName));
    }
    
    /**
     * ファイルから説明文を抽出
     */
    extractDescription(lines) {
        let foundTitle = false;
        
        for (const line of lines) {
            // タイトル（# ヘッダー）が見つかった後の最初の段落を取得
            if (line.match(/^#\s+/)) {
                foundTitle = true;
                continue;
            }
            
            if (foundTitle && line.trim() && !line.match(/^[#\-*]/)) {
                const desc = line.trim().substring(0, 100);
                return desc.length < line.trim().length ? desc + '...' : desc;
            }
        }
        
        return '';
    }
    
    /**
     * タイトルに適切な絵文字を追加
     */
    addEmojiIfNeeded(title) {
        if (title.match(/^[🎯🚀📝🏗️👨‍💻⚙️📖🎫📋🔧🔄]/)) {
            return title; // 既に絵文字がある
        }
        
        // キーワードベースで絵文字を付与
        const emojiMap = {
            'quick': '⚡', 'start': '⚡', 'クイック': '⚡',
            'architecture': '🏗️', 'アーキテクチャ': '🏗️',
            'setup': '🔧', 'セットアップ': '🔧', '設定': '🔧',
            'guide': '📖', 'ガイド': '📖',
            'ci/cd': '🔄', 'deploy': '🚀', 'デプロイ': '🚀',
            'issue': '🎫', 'plan': '📋', 'プラン': '📋',
            'coding': '📝', 'コーディング': '📝',
            'technical': '⚙️', '技術': '⚙️',
            'agent': '🤖', 'エージェント': '🤖'
        };
        
        const lowerTitle = title.toLowerCase();
        for (const [keyword, emoji] of Object.entries(emojiMap)) {
            if (lowerTitle.includes(keyword)) {
                return `${emoji} ${title}`;
            }
        }
        
        return `📄 ${title}`;
    }
    
    /**
     * ファイル名を読みやすい形式に変換
     */
    formatFileName(fileName) {
        return fileName
            .replace(/-/g, ' ')
            .replace(/([a-z])([A-Z])/g, '$1 $2')
            .split(' ')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    }
    
    /**
     * ディレクトリ名かどうかをチェック
     */
    isDirectoryName(fileName) {
        const baseName = path.basename(fileName, '.md');
        const categories = Object.keys(this.categoryConfig);
        return categories.includes(baseName);
    }
    
    /**
     * navigation.json を生成
     */
    async generateNavigationJson(docStructure) {
        const navigation = {
            title: "GenieUs Documentation",
            subtitle: "見えない成長に、光をあてる。不安な毎日を、自信に変える。",
            sections: []
        };
        
        // クイックスタートセクションを特別に作成
        if (docStructure.quickstart || this.hasQuickStartFiles(docStructure)) {
            navigation.sections.push({
                id: "quickstart",
                title: "🚀 すぐ始める",
                items: this.buildQuickStartItems(docStructure)
            });
        }
        
        // 各カテゴリをソートして追加
        const sortedCategories = Object.keys(docStructure)
            .filter(cat => cat !== 'root' && cat !== 'quickstart')
            .sort((a, b) => {
                const orderA = this.categoryConfig[a]?.order || 999;
                const orderB = this.categoryConfig[b]?.order || 999;
                return orderA - orderB;
            });
        
        for (const category of sortedCategories) {
            const config = this.categoryConfig[category];
            if (!config) continue;
            
            const items = docStructure[category].map(file => ({
                title: file.title,
                file: file.file,
                ...(file.description && { description: file.description })
            }));
            
            if (items.length > 0) {
                navigation.sections.push({
                    id: category,
                    title: config.title,
                    items
                });
            }
        }
        
        // navigation.json を保存
        fs.writeFileSync(this.navigationFile, JSON.stringify(navigation, null, 2), 'utf-8');
        console.log(`💾 navigation.json を更新: ${navigation.sections.length}セクション`);
    }
    
    /**
     * クイックスタート項目を構築
     */
    buildQuickStartItems(docStructure) {
        const items = [
            { title: "📝 ホーム", file: "", description: "ドキュメントホーム" }
        ];
        
        // 重要ファイルを追加
        const importantFiles = [
            'development/quick-start.md',
            'development/coding-standards.md', 
            'architecture/overview.md'
        ];
        
        for (const filePath of importantFiles) {
            const [category, fileName] = filePath.split('/');
            const file = docStructure[category]?.find(f => f.file === filePath);
            if (file) {
                items.push({
                    title: file.title,
                    file: file.file,
                    description: file.description
                });
            }
        }
        
        return items;
    }
    
    /**
     * クイックスタートファイルがあるかチェック
     */
    hasQuickStartFiles(docStructure) {
        const quickStartFiles = ['development/quick-start.md', 'development/coding-standards.md'];
        return quickStartFiles.some(filePath => {
            const [category] = filePath.split('/');
            return docStructure[category]?.some(f => f.file === filePath);
        });
    }
    
    /**
     * index.html を生成（再生成スクリプトを呼び出し）
     */
    async generateIndexHtml() {
        const { generateFromNavigationJson } = require('./regenerate-index-html.js');
        generateFromNavigationJson();
    }
    
    
    /**
     * 総ファイル数をカウント
     */
    countTotalFiles(structure) {
        return Object.values(structure).reduce((total, files) => total + files.length, 0);
    }
}

// CLI実行
if (require.main === module) {
    const generator = new DocsNavigationGenerator();
    
    // コマンドライン引数処理
    const args = process.argv.slice(2);
    const watchMode = args.includes('--watch') || args.includes('-w');
    
    if (watchMode) {
        console.log('👀 ファイル監視モードで実行中...');
        
        // 初回実行
        generator.generate();
        
        // ファイル監視開始
        const chokidar = require('chokidar');
        const watcher = chokidar.watch(generator.docsDir + '/**/*.md', {
            ignored: /node_modules/,
            persistent: true
        });
        
        let timeout;
        watcher.on('change', () => {
            clearTimeout(timeout);
            timeout = setTimeout(() => {
                console.log('📝 ファイル変更を検出、再生成中...');
                generator.generate();
            }, 1000);
        });
        
        console.log('Press Ctrl+C to stop watching...');
        
    } else {
        generator.generate();
    }
}

module.exports = DocsNavigationGenerator;