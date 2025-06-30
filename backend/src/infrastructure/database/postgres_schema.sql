-- PostgreSQL Schema for GenieUs Database
-- SQLite互換データベーススキーマ定義（既存SQLite構造に合わせて修正）

-- Users テーブル（SQLite互換）
CREATE TABLE IF NOT EXISTS users (
    google_id VARCHAR(255) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    picture_url TEXT,
    locale VARCHAR(50),
    verified_email BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT users_google_id_check CHECK (google_id <> ''),
    CONSTRAINT users_email_check CHECK (email <> ''),
    CONSTRAINT users_name_check CHECK (name <> '')
);

-- Users テーブルインデックス
CREATE INDEX IF NOT EXISTS idx_users_google_id ON users(google_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Family Info テーブル（SQLite互換）
CREATE TABLE IF NOT EXISTS family_info (
    family_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    parent_name VARCHAR(255) NOT NULL,
    family_structure TEXT,
    concerns TEXT,
    living_area TEXT,
    children TEXT,  -- JSON形式で保存
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(google_id) ON DELETE CASCADE,
    CONSTRAINT family_info_family_id_check CHECK (family_id <> ''),
    CONSTRAINT family_info_user_id_check CHECK (user_id <> ''),
    CONSTRAINT family_info_parent_name_check CHECK (parent_name <> '')
);

-- Family Info テーブルインデックス
CREATE INDEX IF NOT EXISTS idx_family_info_user_id ON family_info(user_id);
CREATE INDEX IF NOT EXISTS idx_family_info_parent_name ON family_info(parent_name);

-- Growth Records テーブル（SQLite互換）
CREATE TABLE IF NOT EXISTS growth_records (
    id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    child_id VARCHAR(255) NOT NULL,
    record_date TEXT NOT NULL,
    height_cm DECIMAL(5,2),
    weight_kg DECIMAL(5,2),
    head_circumference_cm DECIMAL(5,2),
    chest_circumference_cm DECIMAL(5,2),
    milestone_description TEXT,
    notes TEXT,
    photo_paths TEXT,  -- JSON array
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(google_id) ON DELETE CASCADE,
    CONSTRAINT growth_records_id_check CHECK (id <> ''),
    CONSTRAINT growth_records_user_id_check CHECK (user_id <> ''),
    CONSTRAINT growth_records_child_id_check CHECK (child_id <> ''),
    CONSTRAINT growth_records_height_check CHECK (height_cm IS NULL OR height_cm > 0),
    CONSTRAINT growth_records_weight_check CHECK (weight_kg IS NULL OR weight_kg > 0)
);

-- Growth Records テーブルインデックス
CREATE INDEX IF NOT EXISTS idx_growth_records_user_id ON growth_records(user_id);
CREATE INDEX IF NOT EXISTS idx_growth_records_child_id ON growth_records(child_id);
CREATE INDEX IF NOT EXISTS idx_growth_records_date ON growth_records(record_date);

-- Memory Records テーブル（SQLite互換）
CREATE TABLE IF NOT EXISTS memory_records (
    id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    child_id VARCHAR(255),
    title VARCHAR(500) NOT NULL,
    description TEXT,
    date TEXT NOT NULL,
    tags TEXT,  -- JSON array
    media_paths TEXT,  -- JSON array
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(google_id) ON DELETE CASCADE,
    CONSTRAINT memory_records_id_check CHECK (id <> ''),
    CONSTRAINT memory_records_user_id_check CHECK (user_id <> ''),
    CONSTRAINT memory_records_title_check CHECK (title <> '')
);

-- Memory Records テーブルインデックス
CREATE INDEX IF NOT EXISTS idx_memory_records_user_id ON memory_records(user_id);
CREATE INDEX IF NOT EXISTS idx_memory_records_child_id ON memory_records(child_id);
CREATE INDEX IF NOT EXISTS idx_memory_records_date ON memory_records(date);
CREATE INDEX IF NOT EXISTS idx_memory_records_title ON memory_records(title);

-- Meal Records テーブル（SQLite互換）
CREATE TABLE IF NOT EXISTS meal_records (
    id VARCHAR(255) PRIMARY KEY,
    child_id VARCHAR(255) NOT NULL,
    meal_name VARCHAR(255) NOT NULL,
    meal_type VARCHAR(50) NOT NULL,
    detected_foods TEXT,  -- JSON形式
    nutrition_info TEXT,  -- JSON形式
    timestamp TEXT NOT NULL,
    detection_source VARCHAR(100) NOT NULL,
    confidence DECIMAL(3,2) NOT NULL,
    image_path TEXT,
    notes TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    CONSTRAINT meal_records_id_check CHECK (id <> ''),
    CONSTRAINT meal_records_child_id_check CHECK (child_id <> ''),
    CONSTRAINT meal_records_meal_name_check CHECK (meal_name <> ''),
    CONSTRAINT meal_records_meal_type_check CHECK (meal_type <> ''),
    CONSTRAINT meal_records_confidence_check CHECK (confidence >= 0 AND confidence <= 1)
);

-- Meal Records テーブルインデックス
CREATE INDEX IF NOT EXISTS idx_meal_records_child_id ON meal_records(child_id);
CREATE INDEX IF NOT EXISTS idx_meal_records_meal_type ON meal_records(meal_type);
CREATE INDEX IF NOT EXISTS idx_meal_records_timestamp ON meal_records(timestamp);

-- Schedule Records テーブル（SQLite互換）
CREATE TABLE IF NOT EXISTS schedule_records (
    id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    title VARCHAR(500) NOT NULL,
    date TEXT,
    time TEXT,
    type VARCHAR(100),
    location TEXT,
    description TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'upcoming',
    created_by VARCHAR(100) NOT NULL DEFAULT 'genie',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(google_id) ON DELETE CASCADE,
    CONSTRAINT schedule_records_id_check CHECK (id <> ''),
    CONSTRAINT schedule_records_user_id_check CHECK (user_id <> ''),
    CONSTRAINT schedule_records_title_check CHECK (title <> '')
);

-- Schedule Records テーブルインデックス
CREATE INDEX IF NOT EXISTS idx_schedule_records_user_id ON schedule_records(user_id);
CREATE INDEX IF NOT EXISTS idx_schedule_records_date ON schedule_records(date);
CREATE INDEX IF NOT EXISTS idx_schedule_records_type ON schedule_records(type);
CREATE INDEX IF NOT EXISTS idx_schedule_records_status ON schedule_records(status);

-- Effort Reports テーブル（SQLite互換）
CREATE TABLE IF NOT EXISTS effort_reports (
    report_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    period_days INTEGER NOT NULL DEFAULT 7,
    effort_count INTEGER NOT NULL DEFAULT 0,
    score DECIMAL(3,1) NOT NULL DEFAULT 0.0,
    highlights TEXT,
    categories TEXT,
    summary TEXT NOT NULL DEFAULT '',
    achievements TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(google_id) ON DELETE CASCADE,
    CONSTRAINT effort_reports_report_id_check CHECK (report_id <> ''),
    CONSTRAINT effort_reports_user_id_check CHECK (user_id <> ''),
    CONSTRAINT effort_reports_period_check CHECK (period_days > 0),
    CONSTRAINT effort_reports_score_check CHECK (score >= 0)
);

-- Effort Reports テーブルインデックス
CREATE INDEX IF NOT EXISTS idx_effort_reports_user_id ON effort_reports(user_id);
CREATE INDEX IF NOT EXISTS idx_effort_reports_score ON effort_reports(score);
CREATE INDEX IF NOT EXISTS idx_effort_reports_created_at ON effort_reports(created_at);

-- Child Records テーブル（SQLite互換）
CREATE TABLE IF NOT EXISTS child_records (
    id VARCHAR(255) PRIMARY KEY,
    child_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    value DECIMAL(10,2),
    unit VARCHAR(50),
    text_data TEXT,
    metadata TEXT,  -- JSON形式
    confidence DECIMAL(3,2) DEFAULT 1.0,
    source VARCHAR(100) DEFAULT 'manual',
    parent_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(google_id) ON DELETE CASCADE,
    CONSTRAINT child_records_id_check CHECK (id <> ''),
    CONSTRAINT child_records_child_id_check CHECK (child_id <> ''),
    CONSTRAINT child_records_user_id_check CHECK (user_id <> ''),
    CONSTRAINT child_records_event_type_check CHECK (event_type <> '')
);

-- Child Records テーブルインデックス
CREATE INDEX IF NOT EXISTS idx_child_records_child_id ON child_records(child_id);
CREATE INDEX IF NOT EXISTS idx_child_records_user_id ON child_records(user_id);
CREATE INDEX IF NOT EXISTS idx_child_records_event_type ON child_records(event_type);
CREATE INDEX IF NOT EXISTS idx_child_records_timestamp ON child_records(timestamp);

-- Migrations テーブル（SQLite互換）
CREATE TABLE IF NOT EXISTS migrations (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    executed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 更新時刻自動更新のトリガー関数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 各テーブルに更新時刻自動更新トリガーを設定（TIMESTAMP列があるテーブルのみ）
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_family_info_updated_at ON family_info;
CREATE TRIGGER update_family_info_updated_at BEFORE UPDATE ON family_info FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_growth_records_updated_at ON growth_records;
CREATE TRIGGER update_growth_records_updated_at BEFORE UPDATE ON growth_records FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_memory_records_updated_at ON memory_records;
CREATE TRIGGER update_memory_records_updated_at BEFORE UPDATE ON memory_records FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_child_records_updated_at ON child_records;
CREATE TRIGGER update_child_records_updated_at BEFORE UPDATE ON child_records FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- デモ用初期データ挿入
INSERT INTO users (google_id, email, name, picture_url, verified_email) VALUES 
('demo_user_001', 'demo@genieus.com', 'デモユーザー', 'https://via.placeholder.com/150', true)
ON CONFLICT (google_id) DO NOTHING;

INSERT INTO users (google_id, email, name, picture_url, verified_email) VALUES 
('frontend_user', 'frontend@genieus.com', 'フロントエンドユーザー', 'https://via.placeholder.com/150', true)
ON CONFLICT (google_id) DO NOTHING;

-- デモ用家族データ
INSERT INTO family_info (family_id, user_id, parent_name, family_structure, concerns, living_area, children) VALUES 
('demo_family_001', 'demo_user_001', 'デモママ', '核家族', '健康な成長', '東京都', '[{"name": "太郎", "age": 3, "birthdate": "2021-03-15"}, {"name": "花子", "age": 1, "birthdate": "2023-06-20"}]')
ON CONFLICT (family_id) DO NOTHING;

INSERT INTO family_info (family_id, user_id, parent_name, family_structure, concerns, living_area, children) VALUES 
('frontend_family_001', 'frontend_user', 'テストママ', '核家族', '発達支援', '神奈川県', '[{"name": "テスト太郎", "age": 4, "birthdate": "2020-12-01"}, {"name": "テスト花子", "age": 2, "birthdate": "2022-08-15"}]')
ON CONFLICT (family_id) DO NOTHING;

-- データベース初期化完了確認
SELECT 'PostgreSQL Database Schema (SQLite Compatible) Initialized Successfully' as status;