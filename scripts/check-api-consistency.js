#!/usr/bin/env node

/**
 * API Endpoint Consistency Checker
 * 
 * フロントエンドとバックエンドのAPI URL整合性をチェックするスクリプト
 * 
 * 使用方法:
 * node scripts/check-api-consistency.js
 * npm run api:check
 */

const fs = require('fs');
const path = require('path');

// カラー出力用
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
};

class APIConsistencyChecker {
  constructor() {
    this.mappingFile = path.join(__dirname, '..', 'api-endpoints-mapping.json');
    this.mapping = null;
    this.errors = [];
    this.warnings = [];
  }

  /**
   * メイン実行関数
   */
  async run() {
    console.log(`${colors.cyan}${colors.bright}🔍 API Endpoint Consistency Checker${colors.reset}`);
    console.log(`${colors.blue}================================================${colors.reset}\n`);

    try {
      await this.loadMapping();
      await this.performChecks();
      this.generateReport();
      
      return this.errors.length === 0;
    } catch (error) {
      console.error(`${colors.red}❌ エラー: ${error.message}${colors.reset}`);
      return false;
    }
  }

  /**
   * マッピングファイルを読み込み
   */
  async loadMapping() {
    if (!fs.existsSync(this.mappingFile)) {
      throw new Error(`マッピングファイルが見つかりません: ${this.mappingFile}`);
    }

    const content = fs.readFileSync(this.mappingFile, 'utf8');
    this.mapping = JSON.parse(content);
    
    console.log(`${colors.green}✅ マッピングファイルを読み込みました${colors.reset}`);
    console.log(`   ファイル: ${this.mappingFile}`);
    console.log(`   バージョン: ${this.mapping.version}`);
    console.log(`   最終更新: ${this.mapping.last_updated}\n`);
  }

  /**
   * 整合性チェックを実行
   */
  async performChecks() {
    console.log(`${colors.yellow}🔍 整合性チェック実行中...${colors.reset}\n`);

    // 1. 設定チェック
    this.checkConfiguration();

    // 2. エンドポイント整合性チェック
    this.checkEndpointConsistency();

    // 3. ファイル存在チェック
    await this.checkFileExistence();

    // 4. 既知の問題チェック
    this.checkKnownIssues();
  }

  /**
   * 設定チェック
   */
  checkConfiguration() {
    console.log(`${colors.blue}📋 設定チェック${colors.reset}`);

    const { backend, frontend } = this.mapping.configuration;

    // バックエンド設定チェック
    if (!backend.base_url) {
      this.errors.push('バックエンドのbase_urlが設定されていません');
    }

    if (!backend.api_prefix) {
      this.errors.push('バックエンドのapi_prefixが設定されていません');
    }

    // フロントエンド設定チェック
    if (!frontend.default_api_base_url) {
      this.errors.push('フロントエンドのdefault_api_base_urlが設定されていません');
    }

    // CORS設定チェック
    if (!backend.cors_origins || backend.cors_origins.length === 0) {
      this.warnings.push('CORS originsが設定されていません');
    }

    console.log(`   ${colors.green}✅ 設定チェック完了${colors.reset}\n`);
  }

  /**
   * エンドポイント整合性チェック
   */
  checkEndpointConsistency() {
    console.log(`${colors.blue}🔗 エンドポイント整合性チェック${colors.reset}`);

    let checkedEndpoints = 0;
    let inconsistentEndpoints = 0;

    Object.entries(this.mapping.endpoint_mappings).forEach(([category, config]) => {
      console.log(`   📂 ${config.category} (${category})`);

      config.endpoints.forEach(endpoint => {
        checkedEndpoints++;

        // ステータスチェック
        if (endpoint.status && endpoint.status.includes('⚠️')) {
          inconsistentEndpoints++;
          this.warnings.push(`${category}.${endpoint.name}: ${endpoint.status}`);
          console.log(`     ${colors.yellow}⚠️  ${endpoint.name}: ${endpoint.status}${colors.reset}`);
        } else if (endpoint.status && endpoint.status.includes('✅')) {
          console.log(`     ${colors.green}✅ ${endpoint.name}: OK${colors.reset}`);
        } else {
          this.warnings.push(`${category}.${endpoint.name}: ステータス未設定`);
          console.log(`     ${colors.yellow}❓ ${endpoint.name}: ステータス未設定${colors.reset}`);
        }

        // メソッド整合性チェック
        if (endpoint.frontend_usage) {
          endpoint.frontend_usage.forEach(usage => {
            if (usage.method !== endpoint.backend_method) {
              this.errors.push(
                `${category}.${endpoint.name}: HTTPメソッド不一致 ` +
                `(Frontend: ${usage.method}, Backend: ${endpoint.backend_method})`
              );
            }
          });
        }
      });
    });

    console.log(`   ${colors.bright}📊 チェック結果: ${checkedEndpoints}個中${inconsistentEndpoints}個に不整合${colors.reset}\n`);
  }

  /**
   * ファイル存在チェック
   */
  async checkFileExistence() {
    console.log(`${colors.blue}📁 ファイル存在チェック${colors.reset}`);

    const projectRoot = path.join(__dirname, '..');
    let checkedFiles = 0;
    let missingFiles = 0;

    Object.entries(this.mapping.endpoint_mappings).forEach(([category, config]) => {
      config.endpoints.forEach(endpoint => {
        // バックエンドファイルチェック
        if (endpoint.backend_file) {
          checkedFiles++;
          const backendPath = path.join(projectRoot, endpoint.backend_file);
          if (!fs.existsSync(backendPath)) {
            missingFiles++;
            this.errors.push(`バックエンドファイルが見つかりません: ${endpoint.backend_file}`);
            console.log(`     ${colors.red}❌ ${endpoint.backend_file}${colors.reset}`);
          } else {
            console.log(`     ${colors.green}✅ ${endpoint.backend_file}${colors.reset}`);
          }
        }

        // フロントエンドファイルチェック
        if (endpoint.frontend_usage) {
          endpoint.frontend_usage.forEach(usage => {
            checkedFiles++;
            const frontendPath = path.join(projectRoot, usage.file);
            if (!fs.existsSync(frontendPath)) {
              missingFiles++;
              this.errors.push(`フロントエンドファイルが見つかりません: ${usage.file}`);
              console.log(`     ${colors.red}❌ ${usage.file}${colors.reset}`);
            } else {
              console.log(`     ${colors.green}✅ ${usage.file}${colors.reset}`);
            }
          });
        }
      });
    });

    console.log(`   ${colors.bright}📊 ファイルチェック結果: ${checkedFiles}個中${missingFiles}個が見つかりません${colors.reset}\n`);
  }

  /**
   * 既知の問題チェック
   */
  checkKnownIssues() {
    console.log(`${colors.blue}⚡ 既知の問題チェック${colors.reset}`);

    if (this.mapping.issues && this.mapping.issues.length > 0) {
      this.mapping.issues.forEach(issue => {
        console.log(`   ${colors.yellow}⚠️  ${issue.category}: ${issue.issue}${colors.reset}`);
        console.log(`       説明: ${issue.description}`);
        console.log(`       推奨: ${issue.recommendation}`);

        if (issue.severity === 'error') {
          this.errors.push(`${issue.category}: ${issue.issue}`);
        } else {
          this.warnings.push(`${issue.category}: ${issue.issue}`);
        }
      });
    } else {
      console.log(`   ${colors.green}✅ 既知の問題はありません${colors.reset}`);
    }

    console.log('');
  }

  /**
   * レポート生成
   */
  generateReport() {
    console.log(`${colors.magenta}${colors.bright}📋 整合性チェック結果${colors.reset}`);
    console.log(`${colors.magenta}================================================${colors.reset}`);

    // 統計情報
    const stats = this.mapping.statistics;
    if (stats) {
      console.log(`${colors.cyan}📊 統計情報:${colors.reset}`);
      console.log(`   総エンドポイント数: ${stats.total_endpoints}`);
      console.log(`   整合性OK: ${stats.consistent_endpoints}`);
      console.log(`   不整合: ${stats.inconsistent_endpoints}`);
      console.log(`   整合性率: ${stats.consistency_rate}`);
      console.log('');
    }

    // エラー表示
    if (this.errors.length > 0) {
      console.log(`${colors.red}${colors.bright}❌ エラー (${this.errors.length}件):${colors.reset}`);
      this.errors.forEach((error, index) => {
        console.log(`   ${index + 1}. ${error}`);
      });
      console.log('');
    }

    // 警告表示
    if (this.warnings.length > 0) {
      console.log(`${colors.yellow}${colors.bright}⚠️  警告 (${this.warnings.length}件):${colors.reset}`);
      this.warnings.forEach((warning, index) => {
        console.log(`   ${index + 1}. ${warning}`);
      });
      console.log('');
    }

    // 結果サマリー
    if (this.errors.length === 0 && this.warnings.length === 0) {
      console.log(`${colors.green}${colors.bright}✅ すべてのチェックが正常に完了しました！${colors.reset}`);
    } else if (this.errors.length === 0) {
      console.log(`${colors.yellow}${colors.bright}⚠️  警告がありますが、重大な問題はありません${colors.reset}`);
    } else {
      console.log(`${colors.red}${colors.bright}❌ 修正が必要なエラーがあります${colors.reset}`);
    }

    console.log(`${colors.magenta}================================================${colors.reset}\n`);
  }
}

// スクリプト実行
if (require.main === module) {
  const checker = new APIConsistencyChecker();
  checker.run().then(success => {
    process.exit(success ? 0 : 1);
  });
}

module.exports = APIConsistencyChecker;