import psycopg2
import os

def get_env_var(var_name):
    value = os.getenv(var_name)
    if value is None:
        raise ValueError(f"CRITICAL: Environment variable {var_name} is not set.")
    return value

DB_CONFIG = {
    "host": get_env_var("DB_HOST"),
    "port": int(get_env_var("DB_PORT")),
    "dbname": get_env_var("DB_NAME"),
    "user": get_env_var("DB_USER"),
    "password": get_env_var("DB_PASSWORD"),
}

class UserRepository:
    @staticmethod
    def create_user(user_data):
        conn = None
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor()

            query = """
                INSERT INTO users (id, organization_id, company_id, name, email, role, cognito_id, created_at)
                VALUES (
                    (SELECT COALESCE(MAX(id), 0) + 1 FROM users), 
                    %(organization_id)s, %(company_id)s, %(name)s, %(email)s, %(role)s, %(cognito_id)s, %(created_at)s
                ) RETURNING id, name, email, role, created_at;
            """
            
            cursor.execute(query, user_data)
            new_user = cursor.fetchone()
            conn.commit()

            return {
                "id": new_user[0],
                "name": new_user[1],
                "email": new_user[2],
                "role": new_user[3],
                "created_at": str(new_user[4])
            }

        except Exception as e:
            if conn:
                conn.rollback()
            raise Exception(f"Database error: {str(e)}")
        finally:
            if conn:
                cursor.close()
                conn.close()

    @staticmethod
    def get_users_by_organization(org_id, company_id,page, limit):
        conn = None
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor()
            
            offset = (page - 1) * limit
            
            count_query = """
                SELECT COUNT(*)
                FROM users
                WHERE organization_id = %s AND company_id = %s;
            """
            cursor.execute(count_query, (org_id, company_id))
            total_users = cursor.fetchone()[0]

            query = """
                SELECT id, name, email, role, created_at
                FROM users
                WHERE organization_id = %s and company_id = %s
                ORDER BY id
                LIMIT %s OFFSET %s;
            """
            cursor.execute(query, (org_id, company_id, limit, offset))
            rows = cursor.fetchall()

            users = [
                {
                    "id": row[0],
                    "name": row[1],
                    "email": row[2],
                    "role": row[3],
                    "created_at": str(row[4])
                }
                for row in rows
            ]
            total_pages = (total_users + limit - 1) // limit
            
            return {
                "users": users,
                "pagination": {
                    "total_users": total_users,
                    "total_pages": total_pages,
                    "current_page": page,
                    "limit": limit
                }
            }

        except Exception as e:
            raise Exception(f"Database error: {str(e)}")
        finally:
            if conn:
                cursor.close()
                conn.close()

    @staticmethod
    def get_user_by_id(org_id,company_id, user_id):
        conn = None
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor()

            query = """
                SELECT id, name, email, role, created_at
                FROM users
                WHERE organization_id = %s AND company_id = %s AND id = %s;
            """
            cursor.execute(query, (org_id, company_id, user_id))
            row = cursor.fetchone()

            if not row:
                return None

            return {
                "id": row[0],
                "name": row[1],
                "email": row[2],
                "role": row[3],
                "created_at": str(row[4])
            }

        except Exception as e:
            raise Exception(f"Database error: {str(e)}")
        finally:
            if conn:
                cursor.close()
                conn.close()
                
    @staticmethod
    def update_user(org_id, user_data):
        conn = None
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor()

            query = """
                UPDATE users
                SET name = %s,
                    email = %s,
                    role = %s,
                    company_id = %s
                WHERE organization_id = %s AND company_id = %s
                AND id = %s
                RETURNING id, name, email, role, created_at;
            """

            cursor.execute(
                query,
                (
                    user_data["name"],
                    user_data["email"],
                    user_data["role"],
                    user_data["company_id"],
                    org_id,
                    user_data["company_id"],
                    user_data["user_id"]
                )
            )

            updated_user = cursor.fetchone()

            if not updated_user:
                return None

            conn.commit()

            return {
                "id": updated_user[0],
                "name": updated_user[1],
                "email": updated_user[2],
                "role": updated_user[3],
                "created_at": str(updated_user[4])
            }

        except Exception as e:
            if conn:
                conn.rollback()
            raise Exception(f"Database error: {str(e)}")
        finally:
            if conn:
                cursor.close()
                conn.close()
                
    @staticmethod
    def delete_user(org_id,company_id, user_id):
        conn = None
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor()

            query = """
                DELETE FROM users
                WHERE organization_id = %s 
                AND company_id = %s
                AND id = %s
                RETURNING id;
            """

            cursor.execute(query, (org_id, company_id, user_id))
            deleted = cursor.fetchone()

            if not deleted:
                return None

            conn.commit()
            return True

        except Exception as e:
            if conn:
                conn.rollback()
            raise Exception(f"Database error: {str(e)}")

        finally:
            if conn:
                cursor.close()
                conn.close()