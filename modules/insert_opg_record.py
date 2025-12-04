import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# -------------------------------------------
# DB CONNECTION
# -------------------------------------------
def get_connection():
    return psycopg2.connect(
        dbname = os.getenv("DB_NAME"),
        user = os.getenv("DB_USER"),
        password = os.getenv("DB_PASSWORD"),
        host = os.getenv("DB_HOST"),
        port = os.getenv("DB_PORT"),
    )

# -------------------------------------------
# INSERT OR UPDATE DATABASE RECORD (UPSERT)
# -------------------------------------------
def insert_opg_record(title, age, img_bytes, label_text,
                      l13, l23, l33, l43):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO OPGs (
            title, age,
            canine_13_length, canine_23_length,
            canine_33_length, canine_43_length,
            opg_image, label_text
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT (title) DO UPDATE SET
            age = EXCLUDED.age,
            canine_13_length = EXCLUDED.canine_13_length,
            canine_23_length = EXCLUDED.canine_23_length,
            canine_33_length = EXCLUDED.canine_33_length,
            canine_43_length = EXCLUDED.canine_43_length,
            opg_image = EXCLUDED.opg_image,
            label_text = EXCLUDED.label_text;
    """, (
        title, age,
        l13, l23, l33, l43,
        img_bytes, label_text
    ))

    conn.commit()
    cur.close()
    conn.close()