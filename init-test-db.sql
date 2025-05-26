-- \c test_db;
-- 
-- CREATE TABLE IF NOT EXISTS employee (
--     id SERIAL PRIMARY KEY,
--     name VARCHAR(100) NOT NULL,
--     position VARCHAR(50) NOT NULL,
--     salary DECIMAL(10,2) NOT NULL
-- );
-- 
-- INSERT INTO employee (name, position, salary) VALUES
-- ('Alice Johnson', 'Software Engineer', 75000.00),
-- ('Bob Smith', 'Data Analyst', 65000.00),
-- ('Charlie Brown', 'Product Manager', 90000.00),
-- ('Diana White', 'HR Manager', 70000.00),
-- ('Ethan Clark', 'DevOps Engineer', 80000.00);
-- 
-- CREATE TABLE IF NOT EXISTS bookstore (
--     id SERIAL PRIMARY KEY,
--     title VARCHAR(200) NOT NULL,
--     author VARCHAR(100) NOT NULL,
--     price DECIMAL(10,2) NOT NULL
-- );
-- 
-- INSERT INTO bookstore (title, author, price) VALUES
-- ('The Pragmatic Programmer', 'Andrew Hunt', 39.99),
-- ('Clean Code', 'Robert C. Martin', 45.50),
-- ('Deep Learning with Python', 'François Chollet', 55.00),
-- ('Introduction to Algorithms', 'Thomas H. Cormen', 60.00),
-- ('The Phoenix Project', 'Gene Kim', 35.00);
-- 

\c test_db;

CREATE TABLE questionsheet (
    timestamp TIMESTAMPTZ,
    question JSONB
);

CREATE TABLE IF NOT EXISTS student_performance (
    student_id TEXT PRIMARY KEY,
    llm_abuse_score FLOAT DEFAULT 0,
    preliminary_performance INT,
    performance_description TEXT,
    good_tally INT DEFAULT 0,
    last_updated TIMESTAMPTZ DEFAULT now()
);

INSERT INTO questionsheet (timestamp, question)
VALUES (
    now(),
    '{
        "1": "Jelaskan perbedaan utama antara sel prokariotik dan sel eukariotik!",
        "2": "Apa fungsi dari organel mitokondria dalam proses metabolisme sel?",
        "3": "Bagaimana proses transport aktif berbeda dari transport pasif dalam membran sel?"
    }'::jsonb
);
