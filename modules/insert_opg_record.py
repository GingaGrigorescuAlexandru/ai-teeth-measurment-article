import psycopg2
import os
from dotenv import load_dotenv

load_dotenv() # Load the environmental variables 

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
def insert_opg_record(title, age, sex,
                      l13, l23, l33, l43, 
                      dist_13_23, dist_33_43, 
                      img_bytes, label_text):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO OPGs (
            title, sex, age,
            canine_13_length, canine_23_length,
            canine_33_length, canine_43_length,
            distance_13_23, distance_33_43,
            opg_image, label_text
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT (title) DO UPDATE SET
            sex = EXCLUDED.sex,
            age = EXCLUDED.age,
            canine_13_length = EXCLUDED.canine_13_length,
            canine_23_length = EXCLUDED.canine_23_length,
            canine_33_length = EXCLUDED.canine_33_length,
            canine_43_length = EXCLUDED.canine_43_length,
            distance_13_23 = EXCLUDED.distance_13_23,
            distance_33_43 = EXCLUDED.distance_33_43,
            opg_image = EXCLUDED.opg_image,
            label_text = EXCLUDED.label_text;
    """, (
        title, sex, age,
        l13, l23, l33, l43,
        dist_13_23, dist_33_43,
        img_bytes, label_text
    ))

    conn.commit()
    cur.close()
    conn.close()
