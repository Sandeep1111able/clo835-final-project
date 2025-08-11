from flask import Flask, render_template, request
from pymysql import connections
import os
import time

app = Flask(__name__)

# Application configuration from environment
DBHOST = os.environ.get("DBHOST", "localhost")
DBUSER = os.environ.get("DBUSER", "root")
DBPWD = os.environ.get("DBPWD", "password")
DATABASE = os.environ.get("DATABASE", "employees")
DBPORT = int(os.environ.get("DBPORT", 3306))
GROUP_NAME = os.environ.get("GROUP_NAME", "Group 9")
SLOGAN = os.environ.get("SLOGAN", "Final Project")
BACKGROUND_IMAGE_URL = os.environ.get("BACKGROUND_IMAGE_URL")  # expects s3://bucket/key or https URL


def s3_to_https(s3_uri: str) -> str:
    if not s3_uri:
        return None
    if s3_uri.startswith("s3://"):
        _, _, rest = s3_uri.partition("s3://")
        bucket, _, key = rest.partition("/")
        if bucket and key:
            return f"https://{bucket}.s3.amazonaws.com/{key}"
    return s3_uri


RESOLVED_BG_URL = s3_to_https(BACKGROUND_IMAGE_URL)


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


@app.route("/")
def home():
    return render_template('index.html', group_name=GROUP_NAME, slogan=SLOGAN, background_image_url=RESOLVED_BG_URL)


@app.route("/about")
def about():
    return render_template('about.html', group_name=GROUP_NAME, slogan=SLOGAN, background_image_url=RESOLVED_BG_URL)


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
            return render_template('addempoutput.html', name=emp_name, group_name=GROUP_NAME, slogan=SLOGAN, background_image_url=RESOLVED_BG_URL)
        except Exception as e:
            return f"An error occurred: {str(e)}", 500
        finally:
            if db_conn:
                db_conn.close()

    return render_template('addemp.html', group_name=GROUP_NAME, slogan=SLOGAN, background_image_url=RESOLVED_BG_URL)


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

            output = {"group_name": GROUP_NAME, "slogan": SLOGAN, "background_image_url": RESOLVED_BG_URL}
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

    return render_template("getemp.html", group_name=GROUP_NAME, slogan=SLOGAN, background_image_url=RESOLVED_BG_URL)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)