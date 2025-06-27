#!/usr/bin/env node

/**
 * API Mapping Updater
 * 
 * バックエンドとフロントエンドを解析してAPI マッピングファイルを自動更新
 * 
 * 使用方法:
 * node scripts/update-api-mapping.js
 * npm run api:update
 */

const fs = require('fs');
const path = require('path');

class APIMappingUpdater {
  constructor() {
    this.projectRoot = path.join(__dirname, '..');
    this.mappingFile = path.join(this.projectRoot, 'api-endpoints-mapping.json');
    this.backendRoutesDir = path.join(this.projectRoot, 'backend', 'src', 'presentation', 'api', 'routes');
    this.frontendApiDir = path.join(this.projectRoot, 'frontend', 'src', 'libs', 'api');
    this.frontendSrcDir = path.join(this.projectRoot, 'frontend', 'src');
  }

  /**
   * メイン実行関数
   */
  async run() {
    console.log('🔄 API Mapping Updater');
    console.log('================================');

    try {
      const mapping = await this.loadCurrentMapping();
      
      console.log('📊 バックエンドエンドポイントを解析中...');
      const backendEndpoints = await this.analyzeBackendEndpoints();
      
      console.log('🔍 フロントエンドAPIコールを解析中...');
      const frontendApiCalls = await this.analyzeFrontendApiCalls();
      
      console.log('🔗 エンドポイントマッピングを更新中...');
      const updatedMapping = this.updateMapping(mapping, backendEndpoints, frontendApiCalls);
      
      console.log('💾 マッピングファイルを保存中...');
      await this.saveMapping(updatedMapping);
      
      console.log('✅ API マッピングの更新が完了しました！');
      
      return true;
    } catch (error) {
      console.error('❌ エラー:', error.message);
      return false;
    }
  }

  /**
   * 現在のマッピングファイルを読み込み
   */
  async loadCurrentMapping() {
    if (fs.existsSync(this.mappingFile)) {
      const content = fs.readFileSync(this.mappingFile, 'utf8');
      return JSON.parse(content);
    } else {
      // デフォルトのマッピング構造を返す
      return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "GenieUs API Endpoints Mapping",
        "description": "フロントエンドとバックエンドのAPI URL整合性管理",
        "version": "1.0.0",
        "last_updated": new Date().toISOString().split('T')[0],
        "configuration": {
          "backend": {
            "base_url": "http://localhost:8000",
            "production_base_url": "${BACKEND_URL}",
            "api_prefix": "/api"
          },
          "frontend": {
            "base_url": "http://localhost:3000",
            "api_base_url_env": "NEXT_PUBLIC_API_URL",
            "default_api_base_url": "http://localhost:8000"
          }
        },
        "endpoint_mappings": {},
        "issues": [],
        "statistics": {}
      };
    }
  }

  /**
   * バックエンドエンドポイントを解析
   */
  async analyzeBackendEndpoints() {
    const endpoints = [];
    
    if (!fs.existsSync(this.backendRoutesDir)) {
      console.warn(`⚠️  バックエンドルートディレクトリが見つかりません: ${this.backendRoutesDir}`);
      return endpoints;
    }

    const routeFiles = fs.readdirSync(this.backendRoutesDir).filter(file => 
      file.endsWith('.py') && file !== '__init__.py'
    );

    for (const file of routeFiles) {
      const filePath = path.join(this.backendRoutesDir, file);
      const content = fs.readFileSync(filePath, 'utf8');
      
      // ルーターのプレフィックスを抽出
      const prefixMatch = content.match(/router\s*=\s*APIRouter\s*\(\s*prefix\s*=\s*["']([^"']+)["']/);
      const routerPrefix = prefixMatch ? prefixMatch[1] : '';

      // エンドポイント定義を抽出
      const endpointRegex = /@router\.(get|post|put|delete|patch)\s*\(\s*["']([^"']+)["']/g;
      let match;
      
      while ((match = endpointRegex.exec(content)) !== null) {
        const method = match[1].toUpperCase();
        const path = match[2];
        const fullPath = routerPrefix + path;
        
        endpoints.push({
          file: `backend/src/presentation/api/routes/${file}`,
          method,
          path: fullPath,
          routerPrefix,
          localPath: path,
          category: file.replace('.py', '').replace('_', '-')
        });
      }
    }

    console.log(`   見つかったエンドポイント: ${endpoints.length}個`);
    return endpoints;
  }

  /**
   * フロントエンドAPIコールを解析
   */
  async analyzeFrontendApiCalls() {
    const apiCalls = [];

    // TypeScriptファイルを再帰的に検索
    const findTsFiles = (dir) => {
      const files = [];
      if (!fs.existsSync(dir)) return files;

      const items = fs.readdirSync(dir);
      for (const item of items) {
        const fullPath = path.join(dir, item);
        const stat = fs.statSync(fullPath);
        
        if (stat.isDirectory() && !item.startsWith('.') && item !== 'node_modules') {
          files.push(...findTsFiles(fullPath));
        } else if (item.endsWith('.ts') || item.endsWith('.tsx')) {
          files.push(fullPath);
        }
      }
      return files;
    };

    const tsFiles = findTsFiles(this.frontendSrcDir);

    for (const filePath of tsFiles) {
      const content = fs.readFileSync(filePath, 'utf8');
      const relativePath = path.relative(this.projectRoot, filePath);

      // fetch() 呼び出しを抽出
      const fetchRegex = /fetch\s*\(\s*[`"']([^`"']+)[`"']/g;
      let match;

      while ((match = fetchRegex.exec(content)) !== null) {
        const url = match[1];
        
        // API URLかどうかチェック
        if (url.includes('/api/') || url.includes('${API_BASE_URL}') || url.includes('${apiUrl}')) {
          const lines = content.substring(0, match.index).split('\n');
          const lineNumber = lines.length;

          // HTTPメソッドを推定
          const methodMatch = content.substring(match.index - 100, match.index + 100)
            .match(/method\s*:\s*["']([^"']+)["']/);
          const method = methodMatch ? methodMatch[1].toUpperCase() : 'GET';

          apiCalls.push({
            file: relativePath,
            lineNumber,
            method,
            url,
            snippet: content.substring(Math.max(0, match.index - 50), match.index + 100)
          });
        }
      }
    }

    console.log(`   見つかったAPIコール: ${apiCalls.length}個`);
    return apiCalls;
  }

  /**
   * マッピングを更新
   */
  updateMapping(mapping, backendEndpoints, frontendApiCalls) {
    // 更新日時を設定
    mapping.last_updated = new Date().toISOString().split('T')[0];

    // バックエンドエンドポイントでカテゴリを構築
    const categories = {};
    
    for (const endpoint of backendEndpoints) {
      if (!categories[endpoint.category]) {
        categories[endpoint.category] = {
          category: this.getCategoryDisplayName(endpoint.category),
          backend_router_prefix: endpoint.routerPrefix,
          endpoints: []
        };
      }

      // フロントエンドの使用箇所を探す
      const frontendUsage = frontendApiCalls.filter(call => {
        // URLパターンマッチング
        const normalizedBackendPath = endpoint.path.replace(/\{[^}]+\}/g, '[^/?]+');
        const pathRegex = new RegExp(normalizedBackendPath.replace(/\//g, '\\/'));
        return pathRegex.test(call.url) && call.method === endpoint.method;
      });

      categories[endpoint.category].endpoints.push({
        name: this.generateEndpointName(endpoint),
        backend_path: endpoint.path,
        backend_method: endpoint.method,
        backend_file: endpoint.file,
        frontend_usage: frontendUsage.map(usage => ({
          file: usage.file,
          line: usage.lineNumber,
          url_pattern: usage.url,
          method: usage.method
        })),
        status: frontendUsage.length > 0 ? "✅ 整合性OK" : "⚠️ フロントエンドで未使用"
      });
    }

    mapping.endpoint_mappings = categories;

    // 問題を検出
    mapping.issues = this.detectIssues(categories);

    // 統計を更新
    mapping.statistics = this.calculateStatistics(categories);

    return mapping;
  }

  /**
   * カテゴリ表示名を取得
   */
  getCategoryDisplayName(category) {
    const displayNames = {
      'streaming-chat': 'ストリーミングチャット',
      'family': '家族情報管理',
      'agents': 'エージェント情報',
      'growth-records': '成長記録管理',
      'memories': '思い出管理',
      'schedules': 'スケジュール管理',
      'meal-plans': '食事プラン管理',
      'file-upload': 'ファイルアップロード',
      'auth': '認証',
      'effort-reports': '努力レポート',
      'admin': '管理者機能'
    };
    return displayNames[category] || category;
  }

  /**
   * エンドポイント名を生成
   */
  generateEndpointName(endpoint) {
    const pathParts = endpoint.localPath.split('/').filter(part => part && !part.startsWith('{'));
    const methodPrefix = endpoint.method.toLowerCase();
    
    if (pathParts.length === 0) {
      return `${endpoint.category}_${methodPrefix}`;
    }
    
    return `${endpoint.category}_${pathParts.join('_')}`;
  }

  /**
   * 問題を検出
   */
  detectIssues(categories) {
    const issues = [];

    Object.entries(categories).forEach(([categoryKey, category]) => {
      category.endpoints.forEach(endpoint => {
        // フロントエンドで未使用の警告
        if (endpoint.frontend_usage.length === 0) {
          issues.push({
            severity: "warning",
            category: categoryKey,
            issue: "フロントエンドで未使用のエンドポイント",
            description: `${endpoint.backend_path} (${endpoint.backend_method}) はフロントエンドで使用されていません`,
            backend_file: endpoint.backend_file,
            recommendation: "使用されていないエンドポイントを削除するか、フロントエンドで使用してください"
          });
        }

        // プレフィックス不一致の検出
        endpoint.frontend_usage.forEach(usage => {
          const frontendUrl = usage.url_pattern.replace(/\{[^}]+\}/g, '');
          const backendPath = endpoint.backend_path;
          
          if (!frontendUrl.includes(backendPath)) {
            issues.push({
              severity: "error",
              category: categoryKey,
              issue: "URL パス不一致",
              description: `フロントエンド: ${frontendUrl}, バックエンド: ${backendPath}`,
              frontend_file: usage.file,
              backend_file: endpoint.backend_file,
              recommendation: "URLパスを統一してください"
            });
          }
        });
      });
    });

    return issues;
  }

  /**
   * 統計を計算
   */
  calculateStatistics(categories) {
    let totalEndpoints = 0;
    let consistentEndpoints = 0;
    let inconsistentEndpoints = 0;

    Object.values(categories).forEach(category => {
      category.endpoints.forEach(endpoint => {
        totalEndpoints++;
        if (endpoint.status.includes('✅')) {
          consistentEndpoints++;
        } else {
          inconsistentEndpoints++;
        }
      });
    });

    return {
      total_endpoints: totalEndpoints,
      consistent_endpoints: consistentEndpoints,
      inconsistent_endpoints: inconsistentEndpoints,
      consistency_rate: totalEndpoints > 0 ? 
        `${((consistentEndpoints / totalEndpoints) * 100).toFixed(1)}%` : '0%'
    };
  }

  /**
   * マッピングファイルを保存
   */
  async saveMapping(mapping) {
    const jsonContent = JSON.stringify(mapping, null, 2);
    fs.writeFileSync(this.mappingFile, jsonContent, 'utf8');
    console.log(`   保存先: ${this.mappingFile}`);
  }
}

// スクリプト実行
if (require.main === module) {
  const updater = new APIMappingUpdater();
  updater.run().then(success => {
    process.exit(success ? 0 : 1);
  });
}

module.exports = APIMappingUpdater;