import os
import psycopg2

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "host.docker.internal"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "dbname": os.getenv("DB_NAME", "local_dev_db"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "254000"),
}

TABLE_SQL = """

CREATE TABLE "organizations" (
  "id" integer PRIMARY KEY,
  "name" varchar,
  "slug" varchar,
  "plan_type" varchar,
  "created_at" timestamp
);

CREATE TABLE "company" (
  "id" integer PRIMARY KEY,
  "organization_id" INTEGER NOT NULL,
  "name" varchar,
  "created_at" timestamp
);

CREATE TABLE "users" (
  "id" integer PRIMARY KEY,
  "organization_id" integer NOT NULL,
  "company_id" integer NOT NULL,
  "name" varchar,
  "email" varchar,
  "role" varchar,
  "cognito_id" varchar,
  "created_at" timestamp
);

CREATE TABLE "prompts" (
  "id" integer PRIMARY KEY,
  "organization_id" integer NOT NULL,
  "company_id" integer NOT NULL,
  "prompt_name" varchar,
  "prompt_description" text,
  "input_file_type" varchar,
  "output_file_type" varchar,
  "prompt_file_url" varchar,
  "created_at" timestamp
);

CREATE TABLE "conversions" (
  "id" integer PRIMARY KEY,
  "organization_id" integer NOT NULL,
  "user_id" integer NOT NULL,
  "prompt_id" integer,
  "input_file_url" varchar,
  "output_file_url" varchar,
  "status" varchar,
  "created_at" timestamp,
  "completed_at" timestamp
);

CREATE TABLE "usage_logs" (
  "id" integer PRIMARY KEY,
  "user_id" integer,
  "conversion_id" integer,
  "total_tokens" integer,
  "total_credits" integer,
  "created_at" timestamp
);

COMMENT ON COLUMN "users"."role" IS 'org_admin | member | super_admin';
COMMENT ON COLUMN "conversions"."status" IS 'pending | processing | completed | failed';

-- Fixed: removed the ** from ALTER TABLE
ALTER TABLE "company" ADD FOREIGN KEY ("organization_id") REFERENCES "organizations" ("id") DEFERRABLE INITIALLY IMMEDIATE;
ALTER TABLE "users" ADD FOREIGN KEY ("organization_id") REFERENCES "organizations" ("id") DEFERRABLE INITIALLY IMMEDIATE;
ALTER TABLE "prompts" ADD FOREIGN KEY ("organization_id") REFERENCES "organizations" ("id") DEFERRABLE INITIALLY IMMEDIATE;
ALTER TABLE "conversions" ADD FOREIGN KEY ("organization_id") REFERENCES "organizations" ("id") DEFERRABLE INITIALLY IMMEDIATE;
ALTER TABLE "conversions" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id") DEFERRABLE INITIALLY IMMEDIATE;
ALTER TABLE "conversions" ADD FOREIGN KEY ("prompt_id") REFERENCES "prompts" ("id") DEFERRABLE INITIALLY IMMEDIATE;
ALTER TABLE "usage_logs" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id") DEFERRABLE INITIALLY IMMEDIATE;
ALTER TABLE "usage_logs" ADD FOREIGN KEY ("conversion_id") REFERENCES "conversions" ("id") DEFERRABLE INITIALLY IMMEDIATE;
ALTER TABLE "users" ADD FOREIGN KEY ("company_id") REFERENCES "company" ("id") DEFERRABLE INITIALLY IMMEDIATE;
ALTER TABLE "prompts" ADD FOREIGN KEY ("company_id") REFERENCES "company" ("id") DEFERRABLE INITIALLY IMMEDIATE;
"""

def lambda_handler(event, context):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        cursor = conn.cursor()

        cursor.execute(TABLE_SQL)

        cursor.close()
        conn.close()

        return {
            "statusCode": 200,
            "body": "Tables created successfully"
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": str(e)
        }