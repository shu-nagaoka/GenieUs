class DocumentationViewer {
    constructor() {
        this.contentArea = document.getElementById('content-area');
        this.currentFile = '';
        this.searchInput = document.getElementById('search-input');
        this.searchResults = document.getElementById('search-results');
        this.documentIndex = new Map();
        this.fileTimestamps = new Map();
        this.autoRefresh = true;
        this.refreshInterval = 5000; // 5秒ごとにチェック
        this.navigationConfig = null;
        this.init();
    }
    
    async init() {
        // Configure marked.js
        marked.setOptions({
            highlight: function(code, lang) {
                if (Prism.languages[lang]) {
                    return Prism.highlight(code, Prism.languages[lang], lang);
                }
                return code;
            },
            breaks: true,
            gfm: true
        });
        
        // Load navigation configuration
        await this.loadNavigationConfig();
        
        // Build navigation
        this.buildNavigation();
        
        // Add event listeners
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-file]')) {
                e.preventDefault();
                const file = e.target.getAttribute('data-file');
                this.loadFile(file);
            }
        });
        
        // Handle browser back/forward
        window.addEventListener('popstate', (e) => {
            const file = e.state?.file || '';
            this.loadFile(file, false);
        });
        
        // Load initial file from URL hash
        const hash = window.location.hash.substring(1);
        if (hash) {
            this.loadFile(hash);
        }
        
        // Initialize search
        this.setupSearch();
        this.buildDocumentIndex();
        
        // Start auto-refresh
        this.startAutoRefresh();
    }
    
    async loadNavigationConfig() {
        try {
            const response = await fetch('config/navigation.json');
            this.navigationConfig = await response.json();
        } catch (error) {
            console.error('Failed to load navigation config:', error);
            // フォールバック設定
            this.navigationConfig = {
                title: "GenieUs Documentation",
                subtitle: "見えない成長に、光をあてる。不安な毎日を、自信に変える。",
                sections: []
            };
        }
    }
    
    buildNavigation() {
        const sidebar = document.querySelector('.sidebar');
        const navigationHTML = this.navigationConfig.sections.map(section => `
            <div class="nav-section">
                <h3>${section.title}</h3>
                <ul class="nav-list">
                    ${section.items.map(item => `
                        <li><a href="#" data-file="${item.file}">${item.title}</a></li>
                    `).join('')}
                </ul>
            </div>
        `).join('');
        
        // 既存のナビゲーションを更新
        const existingNavSections = sidebar.querySelectorAll('.nav-section');
        existingNavSections.forEach(section => section.remove());
        
        // 新しいナビゲーションを挿入
        const searchSection = sidebar.querySelector('.search-section');
        searchSection.insertAdjacentHTML('afterend', navigationHTML);
    }
    
    startAutoRefresh() {
        if (!this.autoRefresh) return;
        
        setInterval(async () => {
            if (this.currentFile) {
                await this.checkFileUpdate(this.currentFile);
            }
        }, this.refreshInterval);
    }
    
    async checkFileUpdate(filePath) {
        try {
            const response = await fetch('../' + filePath, { method: 'HEAD' });
            if (response.ok) {
                const lastModified = response.headers.get('Last-Modified');
                const currentTimestamp = this.fileTimestamps.get(filePath);
                
                if (lastModified && lastModified !== currentTimestamp) {
                    this.fileTimestamps.set(filePath, lastModified);
                    if (currentTimestamp) { // 初回以外で更新を検知
                        await this.reloadCurrentFile();
                        this.showUpdateNotification();
                    }
                }
            }
        } catch (error) {
            console.warn('Failed to check file update:', error);
        }
    }
    
    async reloadCurrentFile() {
        if (this.currentFile) {
            try {
                const response = await fetch('../' + this.currentFile);
                if (response.ok) {
                    const markdown = await response.text();
                    this.showMarkdown(markdown, this.currentFile);
                    // ドキュメントインデックスも更新
                    const title = document.querySelector(`[data-file="${this.currentFile}"]`)?.textContent?.trim() || 'Document';
                    this.documentIndex.set(this.currentFile, {
                        title,
                        content: markdown,
                        path: this.currentFile
                    });
                }
            } catch (error) {
                console.error('Failed to reload file:', error);
            }
        }
    }
    
    showUpdateNotification() {
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #4caf50;
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            font-size: 0.875rem;
            z-index: 1000;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            animation: slideIn 0.3s ease;
        `;
        notification.innerHTML = '🔄 ドキュメントが更新されました';
        
        // CSS animation
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
        `;
        document.head.appendChild(style);
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideIn 0.3s ease reverse';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
    
    async loadFile(filePath, updateHistory = true) {
        if (filePath === this.currentFile) return;
        
        // Update active navigation
        document.querySelectorAll('.nav-list a').forEach(link => {
            link.classList.toggle('active', link.getAttribute('data-file') === filePath);
        });
        
        if (!filePath) {
            this.showHome();
            this.currentFile = '';
            if (updateHistory) {
                history.pushState({ file: '' }, '', '#');
            }
            return;
        }
        
        this.showLoading();
        
        try {
            const response = await fetch('../' + filePath);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const markdown = await response.text();
            this.showMarkdown(markdown, filePath);
            this.currentFile = filePath;
            
            // ファイルのタイムスタンプを記録
            const lastModified = response.headers.get('Last-Modified');
            if (lastModified) {
                this.fileTimestamps.set(filePath, lastModified);
            }
            
            if (updateHistory) {
                history.pushState({ file: filePath }, '', `#${filePath}`);
            }
            
        } catch (error) {
            this.showError(`ファイルの読み込みに失敗しました: ${error.message}`);
        }
    }
    
    showHome() {
        const quickAccess = this.navigationConfig.sections.find(s => s.id === 'quickstart')?.items || [];
        const quickAccessHTML = quickAccess.slice(1, 4).map(item => `
            <a href="#" class="quick-item" data-file="${item.file}">
                <h3>${item.title}</h3>
                <p>${item.description || ''}</p>
            </a>
        `).join('');
        
        this.contentArea.innerHTML = `
            <div class="home-content">
                <h1>🧞‍♂️ ${this.navigationConfig.title}</h1>
                <p>${this.navigationConfig.subtitle}</p>
                
                <div class="quick-access">
                    ${quickAccessHTML}
                </div>
                
                <div class="auto-refresh-indicator">
                    <span class="indicator-dot ${this.autoRefresh ? 'active' : ''}"></span>
                    自動更新: ${this.autoRefresh ? 'ON' : 'OFF'}
                    <button class="toggle-refresh" onclick="viewer.toggleAutoRefresh()">
                        ${this.autoRefresh ? '停止' : '開始'}
                    </button>
                </div>
            </div>
        `;
    }
    
    toggleAutoRefresh() {
        this.autoRefresh = !this.autoRefresh;
        if (this.autoRefresh) {
            this.startAutoRefresh();
        }
        this.showHome(); // UI更新
    }
    
    showLoading() {
        this.contentArea.innerHTML = `
            <div class="loading">
                <div class="loading-spinner"></div>
                <p>📖 ドキュメントを読み込み中...</p>
            </div>
        `;
    }
    
    showError(message) {
        this.contentArea.innerHTML = `
            <div class="error">
                <h2>❌ エラー</h2>
                <p>${message}</p>
                <button onclick="location.reload()" class="retry-button">🔄 再読み込み</button>
            </div>
        `;
    }
    
    showMarkdown(markdown, filePath) {
        const fileName = filePath.split('/').pop().replace('.md', '');
        const html = marked.parse(markdown);
        
        this.contentArea.innerHTML = `
            <div class="content-header">
                <h1 class="content-title">${fileName}</h1>
                <div class="content-meta">
                    <span class="content-path">📁 ${filePath}</span>
                    <span class="last-updated" id="last-updated">🕒 読み込み中...</span>
                </div>
            </div>
            <div class="markdown-content">${html}</div>
        `;
        
        // 最終更新時刻を表示
        this.updateLastModifiedTime(filePath);
        
        // Scroll to top
        this.contentArea.scrollTop = 0;
        
        // Re-run Prism highlighting
        Prism.highlightAll();
    }
    
    async updateLastModifiedTime(filePath) {
        try {
            const response = await fetch('../' + filePath, { method: 'HEAD' });
            if (response.ok) {
                const lastModified = response.headers.get('Last-Modified');
                if (lastModified) {
                    const date = new Date(lastModified);
                    const formatted = date.toLocaleString('ja-JP');
                    const element = document.getElementById('last-updated');
                    if (element) {
                        element.textContent = `🕒 最終更新: ${formatted}`;
                    }
                }
            }
        } catch (error) {
            console.warn('Failed to get last modified time:', error);
        }
    }
    
    setupSearch() {
        let searchTimeout;
        this.searchInput.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            const query = e.target.value.trim();
            
            if (query.length < 2) {
                this.clearSearchResults();
                return;
            }
            
            searchTimeout = setTimeout(() => {
                this.performSearch(query);
            }, 300);
        });
        
        this.searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.searchInput.value = '';
                this.clearSearchResults();
            }
        });
    }
    
    async buildDocumentIndex() {
        const fileLinks = document.querySelectorAll('[data-file]');
        for (const link of fileLinks) {
            const filePath = link.getAttribute('data-file');
            if (!filePath) continue;
            
            try {
                const response = await fetch('../' + filePath);
                if (response.ok) {
                    const content = await response.text();
                    const title = link.textContent.trim();
                    this.documentIndex.set(filePath, {
                        title,
                        content,
                        path: filePath
                    });
                }
            } catch (error) {
                console.warn(`Failed to index ${filePath}:`, error);
            }
        }
    }
    
    performSearch(query) {
        const results = [];
        const queryLower = query.toLowerCase();
        
        for (const [filePath, doc] of this.documentIndex) {
            const titleMatch = doc.title.toLowerCase().includes(queryLower);
            const contentMatch = doc.content.toLowerCase().includes(queryLower);
            
            if (titleMatch || contentMatch) {
                const snippet = this.extractSnippet(doc.content, query);
                results.push({
                    title: doc.title,
                    path: filePath,
                    snippet,
                    titleMatch
                });
            }
        }
        
        // Sort by relevance (title matches first)
        results.sort((a, b) => {
            if (a.titleMatch && !b.titleMatch) return -1;
            if (!a.titleMatch && b.titleMatch) return 1;
            return 0;
        });
        
        this.displaySearchResults(results, query);
    }
    
    extractSnippet(content, query) {
        const lines = content.split('\n');
        const queryLower = query.toLowerCase();
        
        for (const line of lines) {
            if (line.toLowerCase().includes(queryLower)) {
                const start = Math.max(0, line.toLowerCase().indexOf(queryLower) - 30);
                const snippet = line.substring(start, start + 120);
                return snippet.length < line.length ? '...' + snippet + '...' : snippet;
            }
        }
        
        return content.substring(0, 100) + '...';
    }
    
    displaySearchResults(results, query) {
        if (results.length === 0) {
            this.searchResults.innerHTML = '<div style="padding: 10px; color: #858585; font-size: 0.875rem;">検索結果が見つかりませんでした</div>';
            return;
        }
        
        const html = results.map(result => {
            const highlightedTitle = this.highlightText(result.title, query);
            const highlightedSnippet = this.highlightText(result.snippet, query);
            
            return `
                <div class="search-result-item" data-file="${result.path}">
                    <div class="search-result-title">${highlightedTitle}</div>
                    <div class="search-result-path">${result.path}</div>
                    <div class="search-result-snippet">${highlightedSnippet}</div>
                </div>
            `;
        }).join('');
        
        this.searchResults.innerHTML = html;
        
        // Add click handlers
        this.searchResults.querySelectorAll('.search-result-item').forEach(item => {
            item.addEventListener('click', () => {
                const filePath = item.getAttribute('data-file');
                this.loadFile(filePath);
                this.searchInput.value = '';
                this.clearSearchResults();
            });
        });
    }
    
    highlightText(text, query) {
        const regex = new RegExp(`(${query})`, 'gi');
        return text.replace(regex, '<span class="search-highlight">$1</span>');
    }
    
    clearSearchResults() {
        this.searchResults.innerHTML = '';
    }
}

// Global instance
let viewer;

// Initialize the viewer
document.addEventListener('DOMContentLoaded', () => {
    viewer = new DocumentationViewer();
});