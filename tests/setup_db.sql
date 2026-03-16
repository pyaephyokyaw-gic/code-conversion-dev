-- Run this once in your local PostgreSQL to create the prompts table
CREATE TABLE IF NOT EXISTS "prompts" (
  "id"                  SERIAL PRIMARY KEY,
  "organization_id"     integer NOT NULL,
  "prompt_name"         varchar,
  "prompt_description"  text,
  "prompt_file_url"     varchar,
  "created_at"          timestamp
);
