import psycopg2

def init_postgres(host="localhost", port=5432, user="postgres", password="12345", db_name="GST-Billing"):
    try:
        conn = psycopg2.connect(host=host, port=port, user=user, password=password, dbname="postgres")
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
        exists = cur.fetchone()
        if not exists:
            cur.execute(f'CREATE DATABASE "{db_name}"')
            print(f'[OK] Database "{db_name}" created successfully in PostgreSQL!')
        else:
            print(f'[OK] Database "{db_name}" already exists in PostgreSQL.')
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"[FAIL] Could not connect to PostgreSQL: {e}")
        return False

if __name__ == "__main__":
    init_postgres()
