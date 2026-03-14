CREATE TABLE IF NOT EXISTS tasks (
    id         SERIAL PRIMARY KEY,
    title      VARCHAR(500) NOT NULL,
    priority   VARCHAR(10)  DEFAULT 'medium',
    done       BOOLEAN      DEFAULT FALSE,
    created_at TIMESTAMP    DEFAULT NOW()
);

INSERT INTO tasks (title, priority) VALUES
  ('Setup Docker environment', 'high'),
  ('Learn Docker Compose', 'high'),
  ('Configure Nginx reverse proxy', 'medium'),
  ('Add SSL certificate', 'medium'),
  ('Push image to Docker Hub', 'low');
