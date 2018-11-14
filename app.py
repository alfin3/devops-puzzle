import datetime
import os
import psycopg2

from flask import Flask, render_template

app = Flask(__name__)
app.secret_key = os.environ['APP_SECRET_KEY']

# first bug detection
# worked after setting ports in the nginx service to"8080:80" in the initial code
#@app.route("/", methods=('GET', 'POST'))
#def index():
#    rate = 1
#    return render_template('index.html', rate = rate)

@app.route("/", methods=('GET', 'POST'))
def index():

    # Connect to database
    conn = psycopg2.connect(host='db', database=os.environ['POSTGRES_DB'], user=os.environ['POSTGRES_USER'], password=os.environ['POSTGRES_PASSWORD'])
    cur = conn.cursor()

    print("Update success rates")
    
    # Get numbers of all GET requests grouped by source
    sql_all = """SELECT source, COUNT(*) FROM weblogs GROUP BY source ORDER BY source;"""
    cur.execute(sql_all)
    all_source_num = dict(cur.fetchall())

    # Get numbers of all succesfull requests grouped by source
    sql_success = """SELECT source, COUNT(*) FROM weblogs WHERE status LIKE \'2__\' GROUP BY source ORDER BY source;"""
    cur.execute(sql_success)
    success_source_num = dict(cur.fetchall())

    print("All: ", all_source_num)
    print("Success: ", success_source_num)

    # Determine rates if there was at least one request
    rate = "No entries yet!"
    local_rate = "No entries yet!"
    remote_rate = "No entries yet!"
    if all_source_num['local'] + all_source_num['remote'] != 0:
        rate = str((success_source_num['local'] + success_source_num['remote']) / (all_source_num['local'] + all_source_num['remote']))
    if all_source_num['local'] != 0:
        local_rate = str(success_source_num['local'] / all_source_num['local'])
    if all_source_num['remote'] != 0:
        remote_rate = str(success_source_num['remote'] / all_source_num['remote'])
    return render_template('index.html', rate=rate, local_rate=local_rate, remote_rate=remote_rate)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
