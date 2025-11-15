-- ============================================================================
-- WRESTLING PROMO ANALYZER - DATABASE SCHEMA
-- PostgreSQL 12+
-- Sprint 1 MVP
-- ============================================================================

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- USERS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,

    -- Profile
    full_name VARCHAR(100),
    ring_name VARCHAR(100),

    -- User type (wrestler, trainer, fan, admin)
    user_type VARCHAR(20) DEFAULT 'wrestler',

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE
);

-- Indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_user_type ON users(user_type);

-- ============================================================================
-- VIDEOS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS videos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,

    -- File information
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size_bytes BIGINT NOT NULL,
    mime_type VARCHAR(50) NOT NULL,

    -- Video metadata (populated by ffprobe)
    duration_seconds DECIMAL(10,2),
    width INTEGER,
    height INTEGER,
    codec VARCHAR(50),
    fps DECIMAL(5,2),
    bitrate INTEGER,

    -- Processing status
    status VARCHAR(20) DEFAULT 'uploaded' CHECK (status IN ('uploaded', 'processing', 'completed', 'failed')),

    -- Optional promo metadata
    promo_title VARCHAR(200),
    promo_type VARCHAR(50),  -- heel_promo, face_promo, interview, etc.
    character_type VARCHAR(50),  -- heel, face, tweener
    promo_context TEXT,  -- User notes about the promo

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processing_started_at TIMESTAMP WITH TIME ZONE,
    processing_completed_at TIMESTAMP WITH TIME ZONE
);

-- Indexes
CREATE INDEX idx_videos_user_id ON videos(user_id);
CREATE INDEX idx_videos_status ON videos(status);
CREATE INDEX idx_videos_created_at ON videos(created_at DESC);
CREATE INDEX idx_videos_promo_type ON videos(promo_type);

-- ============================================================================
-- TRANSCRIPTS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS transcripts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    video_id UUID UNIQUE NOT NULL REFERENCES videos(id) ON DELETE CASCADE,

    -- Transcript content
    full_text TEXT NOT NULL,

    -- Timestamped segments from Whisper
    -- Format: [{"start": 0.0, "end": 2.5, "text": "..."}, ...]
    segments JSONB NOT NULL,

    -- Metadata
    language VARCHAR(10) DEFAULT 'en',
    whisper_model VARCHAR(50) DEFAULT 'base',
    word_count INTEGER,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_transcripts_video_id ON transcripts(video_id);
CREATE INDEX idx_transcripts_segments ON transcripts USING GIN (segments);

-- ============================================================================
-- JUDGES TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS judges (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Judge information
    name VARCHAR(100) UNIQUE NOT NULL,
    slug VARCHAR(50) UNIQUE NOT NULL,

    -- Personality
    personality_type VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    evaluation_focus TEXT NOT NULL,

    -- Scoring configuration
    -- Format: {"psychology": 25, "character_work": 20, ...}
    scoring_criteria JSONB NOT NULL,

    -- AI prompts
    system_prompt TEXT NOT NULL,
    user_prompt_template TEXT NOT NULL,

    -- Status
    is_active BOOLEAN DEFAULT true,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_judges_slug ON judges(slug);
CREATE INDEX idx_judges_is_active ON judges(is_active);

-- ============================================================================
-- ANALYSES TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS analyses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    video_id UUID NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
    judge_id UUID NOT NULL REFERENCES judges(id) ON DELETE CASCADE,
    transcript_id UUID NOT NULL REFERENCES transcripts(id) ON DELETE CASCADE,

    -- Overall scores
    overall_score DECIMAL(5,2) NOT NULL CHECK (overall_score >= 0 AND overall_score <= 100),
    overall_grade VARCHAR(2),  -- A, A-, B+, B, B-, C+, C, C-, D, F

    -- Category scores (0-100 scale)
    psychology_score DECIMAL(5,2) CHECK (psychology_score >= 0 AND psychology_score <= 100),
    character_score DECIMAL(5,2) CHECK (character_score >= 0 AND character_score <= 100),
    delivery_score DECIMAL(5,2) CHECK (delivery_score >= 0 AND delivery_score <= 100),
    structure_score DECIMAL(5,2) CHECK (structure_score >= 0 AND structure_score <= 100),
    crowd_connection_score DECIMAL(5,2) CHECK (crowd_connection_score >= 0 AND crowd_connection_score <= 100),
    originality_score DECIMAL(5,2) CHECK (originality_score >= 0 AND originality_score <= 100),

    -- Feedback
    summary TEXT NOT NULL,
    strengths TEXT[] NOT NULL DEFAULT '{}',
    weaknesses TEXT[] NOT NULL DEFAULT '{}',

    -- Timestamped feedback
    -- Format: [{"timestamp": "00:15", "comment": "...", "type": "positive"}, ...]
    timestamped_feedback JSONB NOT NULL DEFAULT '[]',

    -- Recommendations
    specific_recommendations TEXT[] DEFAULT '{}',

    -- Processing metadata
    processing_time_seconds DECIMAL(10,2),
    token_count INTEGER,
    model_version VARCHAR(50),

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Ensure one analysis per judge per video
    UNIQUE(video_id, judge_id)
);

-- Indexes
CREATE INDEX idx_analyses_video_id ON analyses(video_id);
CREATE INDEX idx_analyses_judge_id ON analyses(judge_id);
CREATE INDEX idx_analyses_overall_score ON analyses(overall_score DESC);
CREATE INDEX idx_analyses_created_at ON analyses(created_at DESC);
CREATE INDEX idx_analyses_timestamped_feedback ON analyses USING GIN (timestamped_feedback);

-- ============================================================================
-- PROCESSING_JOBS TABLE (for tracking Celery tasks)
-- ============================================================================

CREATE TABLE IF NOT EXISTS processing_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    video_id UUID NOT NULL REFERENCES videos(id) ON DELETE CASCADE,

    -- Job information
    job_type VARCHAR(50) NOT NULL,  -- extract_metadata, extract_audio, transcribe, analyze
    celery_task_id VARCHAR(255) UNIQUE,

    -- Status
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    progress_percentage INTEGER DEFAULT 0 CHECK (progress_percentage >= 0 AND progress_percentage <= 100),

    -- Error handling
    error_message TEXT,

    -- Timestamps
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_processing_jobs_video_id ON processing_jobs(video_id);
CREATE INDEX idx_processing_jobs_status ON processing_jobs(status);
CREATE INDEX idx_processing_jobs_celery_task_id ON processing_jobs(celery_task_id);

-- ============================================================================
-- SEED DATA: JAKE MORRISON JUDGE
-- ============================================================================

INSERT INTO judges (
    name,
    slug,
    personality_type,
    description,
    evaluation_focus,
    scoring_criteria,
    system_prompt,
    user_prompt_template,
    is_active
) VALUES (
    'Jake Morrison',
    'jake-morrison',
    'old_school_purist',
    'A 30-year veteran of professional wrestling with deep roots in the Memphis territory and extensive experience as a WWE producer and trainer. Known for harsh but fair critiques that focus on fundamentals and psychology.',
    'Wrestling psychology, character consistency, fundamental promo skills, crowd connection',
    '{"psychology": 25, "character_work": 20, "delivery": 20, "story_structure": 15, "crowd_connection": 10, "originality": 10}'::jsonb,
    'You are Jake Morrison, a 30-year veteran wrestling trainer and producer. You have seen it all and have zero patience for shortcuts or gimmicks. Your feedback is harsh but always constructive. You believe wrestling is about making people FEEL something, not just athletic moves or fancy words.',
    'See jake_morrison_prompt.md for complete template',
    true
)
ON CONFLICT (slug) DO NOTHING;

-- ============================================================================
-- TRIGGERS FOR UPDATED_AT
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to users table
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Apply trigger to videos table
CREATE TRIGGER update_videos_updated_at BEFORE UPDATE ON videos
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Apply trigger to judges table
CREATE TRIGGER update_judges_updated_at BEFORE UPDATE ON judges
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- View: Video processing status with analysis summary
CREATE OR REPLACE VIEW video_status_summary AS
SELECT
    v.id AS video_id,
    v.original_filename,
    v.promo_title,
    v.status,
    v.duration_seconds,
    v.created_at,
    v.processing_completed_at,
    COUNT(DISTINCT a.id) AS analysis_count,
    AVG(a.overall_score) AS avg_score,
    EXTRACT(EPOCH FROM (v.processing_completed_at - v.processing_started_at)) AS processing_time_seconds
FROM videos v
LEFT JOIN analyses a ON v.id = a.video_id
GROUP BY v.id, v.original_filename, v.promo_title, v.status, v.duration_seconds,
         v.created_at, v.processing_completed_at, v.processing_started_at;

-- View: Judge performance summary
CREATE OR REPLACE VIEW judge_performance_summary AS
SELECT
    j.id AS judge_id,
    j.name AS judge_name,
    j.personality_type,
    COUNT(a.id) AS total_analyses,
    AVG(a.overall_score) AS avg_score_given,
    AVG(a.processing_time_seconds) AS avg_processing_time,
    MAX(a.created_at) AS last_analysis_at
FROM judges j
LEFT JOIN analyses a ON j.id = a.judge_id
GROUP BY j.id, j.name, j.personality_type;

-- ============================================================================
-- COMMENTS ON TABLES
-- ============================================================================

COMMENT ON TABLE users IS 'User accounts for wrestlers, trainers, and fans';
COMMENT ON TABLE videos IS 'Uploaded wrestling promo videos';
COMMENT ON TABLE transcripts IS 'Whisper AI transcriptions of promo audio';
COMMENT ON TABLE judges IS 'AI judge personalities (Jake Morrison, etc.)';
COMMENT ON TABLE analyses IS 'Judge analysis results with scores and feedback';
COMMENT ON TABLE processing_jobs IS 'Celery background job tracking';

-- ============================================================================
-- SCHEMA VERSION
-- ============================================================================

CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    description TEXT
);

INSERT INTO schema_version (version, description)
VALUES (1, 'Sprint 1 MVP: Core tables for video upload, transcription, and Jake Morrison analysis')
ON CONFLICT (version) DO NOTHING;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Run these after schema creation to verify everything worked:

-- SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;
-- SELECT * FROM judges WHERE slug = 'jake-morrison';
-- SELECT * FROM schema_version;

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
