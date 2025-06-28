#!/usr/bin/env node

/**
 * ドキュメント監視・自動更新スクリプト
 * - docs/配下の.mdファイル変更を監視
 * - 変更検出時に自動的にnavigation.jsonとindex.htmlを更新
 * - 軽量で高速な監視システム
 */

const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');

class DocsWatcher {
    constructor() {
        this.docsDir = path.join(__dirname, '..', 'docs');
        this.generatorScript = path.join(__dirname, 'generate-docs-navigation.js');
        this.debounceTime = 1000; // 1秒のデバウンス
        this.timeout = null;
        this.isGenerating = false;
        
        console.log('📁 監視ディレクトリ:', this.docsDir);
        console.log('🔧 生成スクリプト:', this.generatorScript);
    }
    
    /**
     * 監視開始
     */
    start() {
        console.log('🚀 ドキュメント監視を開始します...');
        
        // 初回生成
        this.generateDocs();
        
        // Node.js組み込みのfs.watchを使用（軽量）
        this.watchDirectory(this.docsDir);
        
        console.log('👀 監視中... (.mdファイルの変更を検出します)');
        console.log('🛑 停止するには Ctrl+C を押してください');
        
        // プロセス終了時のクリーンアップ
        process.on('SIGINT', () => {
            console.log('\n📋 監視を停止しています...');
            process.exit(0);
        });
    }
    
    /**
     * ディレクトリ監視（再帰的）
     */
    watchDirectory(dirPath) {
        try {
            const stats = fs.statSync(dirPath);
            if (!stats.isDirectory()) return;
            
            // ディレクトリ自体を監視
            fs.watch(dirPath, { recursive: false }, (eventType, filename) => {
                if (!filename) return;
                
                const fullPath = path.join(dirPath, filename);
                this.handleFileChange(eventType, fullPath, filename);
            });
            
            // サブディレクトリも再帰的に監視
            const items = fs.readdirSync(dirPath, { withFileTypes: true });
            for (const item of items) {
                if (item.isDirectory() && !this.shouldIgnoreDirectory(item.name)) {
                    this.watchDirectory(path.join(dirPath, item.name));
                }
            }
            
        } catch (error) {
            console.warn(`⚠️ ディレクトリ監視失敗: ${dirPath} - ${error.message}`);
        }
    }
    
    /**
     * ファイル変更ハンドリング
     */
    handleFileChange(eventType, fullPath, filename) {
        // .mdファイルのみ対象
        if (!filename.endsWith('.md')) return;
        
        // 除外ディレクトリチェック
        if (this.shouldIgnorePath(fullPath)) return;
        
        console.log(`📝 ${eventType}: ${path.relative(this.docsDir, fullPath)}`);
        
        // デバウンス処理
        clearTimeout(this.timeout);
        this.timeout = setTimeout(() => {
            this.generateDocs();
        }, this.debounceTime);
    }
    
    /**
     * ドキュメント生成実行
     */
    generateDocs() {
        if (this.isGenerating) {
            console.log('⏳ 既に生成処理実行中...');
            return;
        }
        
        this.isGenerating = true;
        console.log('🔄 ドキュメント自動更新を実行中...');
        
        exec(`node "${this.generatorScript}"`, (error, stdout, stderr) => {
            this.isGenerating = false;
            
            if (error) {
                console.error('❌ 自動更新エラー:', error.message);
                return;
            }
            
            if (stderr) {
                console.warn('⚠️ 警告:', stderr);
            }
            
            if (stdout) {
                console.log(stdout.trim());
            }
            
            console.log(`✅ 自動更新完了 (${new Date().toLocaleTimeString('ja-JP')})\\n`);
        });
    }
    
    /**
     * 除外すべきディレクトリかチェック
     */
    shouldIgnoreDirectory(dirName) {
        const ignoreDirs = [
            'node_modules',
            '.git',
            '.next',
            'web', // web/以下は自動生成対象外
            'assets'
        ];
        return ignoreDirs.includes(dirName);
    }
    
    /**
     * 除外すべきパスかチェック
     */
    shouldIgnorePath(fullPath) {
        const relativePath = path.relative(this.docsDir, fullPath);
        
        // web/ディレクトリは除外
        if (relativePath.startsWith('web/')) return true;
        
        // 隠しファイル除外
        if (path.basename(fullPath).startsWith('.')) return true;
        
        return false;
    }
}

// 直接実行時
if (require.main === module) {
    const watcher = new DocsWatcher();
    watcher.start();
}

module.exports = DocsWatcher;