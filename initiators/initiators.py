from toolbi import SqlDatasource

dest = SqlDatasource()
dest.load('connDest.json')
dest.connect()


#dest.execute("""DROP TABLE Userquestionstate""").commit()

# DBS
dest.execute("""
CREATE TABLE IF NOT EXISTS Dbs (
    id SERIAL PRIMARY KEY,
    db_name VARCHAR(50) NOT NULL,
    available_geos TEXT NULL,
    available_periods TEXT NULL,
    db_source VARCHAR(50) NOT NULL
);
             
CREATE INDEX IF NOT EXISTS idx_db_name ON Dbs(db_name);
""").commit()

# Charts
dest.execute("""
CREATE TABLE IF NOT EXISTS Charts (
    id SERIAL PRIMARY KEY,
    title VARCHAR(50) NOT NULL,
    description TEXT NULL,
    db_name VARCHAR(50) NOT NULL,
    category VARCHAR(20) NULL,
    chart_type VARCHAR(10) NULL,
    vars TEXT NULL,
    vector_dim VECTOR(384)
);
""").commit()

# Categories
dest.execute("""
CREATE TABLE IF NOT EXISTS Categories (
    id SERIAL PRIMARY KEY,
    category VARCHAR(50) NOT NULL,
    description TEXT
);
""").commit()

# Events
dest.execute("""
CREATE TABLE IF NOT EXISTS Events (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    action VARCHAR(10) NOT NULL,
    object_id VARCHAR(50) NOT NULL,
    time TIMESTAMP NOT NULL
);
             
CREATE INDEX IF NOT EXISTS idx_user_id ON Events(user_id);
""").commit()

# Saved
dest.execute("""
CREATE TABLE IF NOT EXISTS Saved (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    object_id VARCHAR(50) NOT NULL,
    time TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_user_id ON Saved(user_id);
""").commit()

# Questions
dest.execute("""
CREATE TABLE IF NOT EXISTS Questions (
    id SERIAL PRIMARY KEY,
    object_id VARCHAR(50) NOT NULL,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    explanation TEXT,
    difficulty SMALLINT,
    sponsor VARCHAR(50),
    sponsor_body TEXT,
    sponsor_link TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);
             
CREATE INDEX IF NOT EXISTS idx_questions_object ON questions(object_id);
""").commit()

# Choices
dest.execute("""
CREATE TABLE IF NOT EXISTS Choices (
    id SERIAL PRIMARY KEY,
    question_id BIGINT NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    is_correct BOOLEAN NOT NULL DEFAULT FALSE
);
             
CREATE INDEX IF NOT EXISTS idx_choices_question ON choices(question_id);
""").commit()

# User question state
dest.execute("""
CREATE TABLE IF NOT EXISTS UserQuestionState (
  user_id BIGINT NOT NULL,
  question_id BIGINT NOT NULL,
  next_due_at TIMESTAMP NOT NULL,
  consecutive_correct SMALLINT DEFAULT 0,
  PRIMARY KEY (user_id, question_id)
);
             
CREATE INDEX IF NOT EXISTS idx_uqs_user_next_due ON UserQuestionState (user_id, next_due_at);
""").commit()

dest.disconnect()