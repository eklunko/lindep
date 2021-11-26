"""
LinDep server application.
"""

import os
import json

from flask import Flask, request, g
import psycopg2

from .tasks import find_lindep_csv, JS_RUNNING, JS_DONE


#------------------------------------------------------------------------------

def get_db():
    """
    Opens a new database connection if there is none yet for the current application context.
    """
    if 'db' not in g:
        conn_string = os.environ['POSTGRES_CONN_STRING']
        conn = psycopg2.connect(conn_string)
        setattr(g, 'db', conn)
    return g.db


def close_db(_error):
    """
    Closes the database again at the end of the request.
    """
    db = g.pop('db', None)
    if db is not None:
        db.close()


#------------------------------------------------------------------------------

def index():
    "View function."
    return """
        <h2>LinDep server.</h2>
    """


def api_upload_csv():
    "View function."
    query = """
    --sql
    insert into jobs (status) values ('new') returning id;
    """
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                row = cur.fetchone()
                job_id = row[0]

        csv_text = request.stream.read().decode('utf-8')
        find_lindep_csv.delay(csv_text, job_id)
        result = {'id': job_id}

    except Exception as e:
        result = {'error': str(e)}

    print(result)
    return result


def api_running_jobs():
    "View function."
    query = """
    --sql
    select count(*) from jobs where status = %(status)s;
    """
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(query, {'status': JS_RUNNING})
                row = cur.fetchone()
                count = row[0]
        result = {'count': count}

    except Exception as e:
        result = {'error': str(e)}

    print(result)
    return result


def api_job_status(job_id):
    "View function."
    query = """
    --sql
    select status, result from jobs where id = %(job_id)s;
    """
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(query, {'job_id': job_id})
                row = cur.fetchone()
                status, jobresult = row
        result = {
            'id': job_id,
            'status': status,
            'result': json.loads(jobresult) if status == JS_DONE else jobresult
        }

    except Exception as e:
        result = {'error': str(e)}

    print(result)
    return result


#------------------------------------------------------------------------------

def create_app():
    """
    Application factory function.
    https://flask.palletsprojects.com/en/2.0.x/patterns/appfactories/
    https://flask.palletsprojects.com/en/2.0.x/tutorial/factory/
    """
    app = Flask(__name__)
    app.config.from_envvar('LINDEP_SETTINGS')

    # Register view functions and other ones.
    app.add_url_rule('/', view_func=index)
    app.add_url_rule('/api/upload_csv', view_func=api_upload_csv, methods=['POST'])
    app.add_url_rule('/api/running_jobs', view_func=api_running_jobs, methods=['GET'])
    app.add_url_rule('/api/job_status/<int:job_id>', view_func=api_job_status, methods=['GET'])
    app.teardown_appcontext(close_db)

    return app
