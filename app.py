from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
import time

app = Flask(__name__)

DBHOST = os.environ.get("DBHOST", "localhost")
DBUSER = os.environ.get("DBUSER", "root")
DBPWD = os.environ.get("DBPWD", "password")
DATABASE = os.environ.get("DATABASE", "employees")
DBPORT = int(os.environ.get("DBPORT", 3306))
GROUP_NAME = os.environ.get("GROUP_NAME", "Group 9")
SLOGAN = os.environ.get("SLOGAN", "Final Project")
S3_BUCKET = os.environ.get("S3_BUCKET")
BACKGROUND_IMAGE_KEY = os.environ.get("BACKGROUND_IMAGE")
AWS_REGION = os.environ.get("AWS_REGION", os.environ.get("AWS_DEFAULT_REGION", "us-east-1"))

def get_db_connection():
    for i in range(10):
        try:
            db_conn = connections.Connection(
                host=DBHOST, port=DBPORT, user=DBUSER, password=DBPWD, db=DATABASE
            )
            print("Database connection successful!")
            return db_conn
        except Exception as e:
            print(f"Database connection attempt {i+1} failed: {e}")
            time.sleep(5)
    return None


def download_background_image_from_s3() -> None:
    if not S3_BUCKET or not BACKGROUND_IMAGE_KEY:
        print("S3 bucket or background image key not configured. Skipping download.")
        return

    target_path = os.path.join("static", "background.jpg")
    
    # Do not check for existence, always try to download to ensure freshness
    # and to recover from previous failed attempts.
    
    s3_url = f"s3://{S3_BUCKET}/{BACKGROUND_IMAGE_KEY}"
    print(f"Attempting to download background image from {s3_url}")

    try:
        os.makedirs("static", exist_ok=True)
        print(f"Ensured static directory exists.")
        
        s3_client = boto3.client("s3", region_name=AWS_REGION)
        s3_client.download_file(S3_BUCKET, BACKGROUND_IMAGE_KEY, target_path)
        
        print(f"Successfully downloaded background image to {target_path}")
    except Exception as e:
        print(f"FATAL: Failed to download background image from {s3_url}: {e}")


@app.route("/")
def home():
    return render_template('index.html', group_name=GROUP_NAME, slogan=SLOGAN)

@app.route("/about")
def about():
    return render_template('about.html', group_name=GROUP_NAME, slogan=SLOGAN)

@app.route("/addemp", methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        db_conn = get_db_connection()
        if not db_conn:
            return "Database service is unavailable.", 503

        try:
            emp_id = request.form['emp_id']
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            primary_skill = request.form['primary_skill']
            location = request.form['location']
            insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
            cursor = db_conn.cursor()
            cursor.execute(insert_sql, (emp_id, first_name, last_name, primary_skill, location))
            db_conn.commit()
            emp_name = f"{first_name} {last_name}"
            return render_template('addempoutput.html', name=emp_name, group_name=GROUP_NAME, slogan=SLOGAN)
        except Exception as e:
            return f"An error occurred: {str(e)}", 500
        finally:
            if db_conn:
                db_conn.close()
    
    return render_template('addemp.html', group_name=GROUP_NAME, slogan=SLOGAN)

@app.route("/getemp", methods=['GET', 'POST'])
def get_employee():
    if request.method == 'POST':
        db_conn = get_db_connection()
        if not db_conn:
            return "Database service is unavailable.", 503

        try:
            emp_id = request.form['emp_id']
            select_sql = "SELECT emp_id, first_name, last_name, primary_skill, location FROM employee WHERE emp_id=%s"
            cursor = db_conn.cursor()
            cursor.execute(select_sql, (emp_id,))
            result = cursor.fetchone()
            
            output = {"group_name": GROUP_NAME, "slogan": SLOGAN}
            if result:
                output.update({
                    "id": result[0],
                    "fname": result[1],
                    "lname": result[2],
                    "interest": result[3],
                    "location": result[4],
                })
            else:
                output["id"] = None
            return render_template("getempoutput.html", **output)
            
        except Exception as e:
            return f"An error occurred: {str(e)}", 500
        finally:
            if db_conn:
                db_conn.close()

    return render_template("getemp.html", group_name=GROUP_NAME, slogan=SLOGAN)


if __name__ == '__main__':
    # Download the background image on startup
    download_background_image_from_s3()
    
    # Start the Flask web server
    app.run(host='0.0.0.0', port=8080, debug=True)