import os
import json

import psycopg2
import numpy as np
import pandas as pd
import sympy

from .celapp import celapp


# Job status
JS_NEW = 'new'
JS_RUNNING = 'running'
JS_DONE = 'done'
JS_ERROR = 'error'


def upload_file_name(job_id):
    "Create a name for the file being uploaded."
    return f'{job_id}.csv'


def update_job_status(job_id, status, result=''):
    """
    Update job status in the database.
    """
    query = """
    --sql
    update jobs set status = %(status)s, result = %(result)s where id = %(job_id)s;
    """
    conn = None
    try:
        conn_string = os.environ['POSTGRES_CONN_STRING']
        conn = psycopg2.connect(conn_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute(query, {'job_id': job_id, 'status': status, 'result': result})
    finally:
        if conn is not None:
            conn.close()


@celapp.task(name='tasks.find_lindep_csv', acks_late=True)
def find_lindep_csv(job_id):
    """
    Celery task to process text from .csv file.
    """
    try:
        update_job_status(job_id, JS_RUNNING)

        # Expected file format:
        # "","col0","col1",...,"colN"
        # "2020-04-13 00:00:00+00:00","0.9166","0.0022",...,"0.6983"
        # "2020-04-13 01:00:00+00:00","0.1147","0.0912",...,"0.3672"
        # ...
        csv_file = os.path.join(os.environ['UPLOAD_AREA'], upload_file_name(job_id))
        df = pd.read_csv(csv_file)

        col_names = find_lindep(df)

    except Exception as e:
        print(f'job #{job_id} error: {e}')
        update_job_status(job_id, JS_ERROR, result=str(e))

    else:
        update_job_status(job_id, JS_DONE, json.dumps(col_names))
        print(f"job #{job_id} complete: [{', '.join(col_names)}]")

    finally:
        os.remove(csv_file)


def find_lindep(df):
    """
    Process dataframe - find linearly dependent columns.
    """
    # Drop first column (date-time string)
    df = df.iloc[:, 1:]

    # Check if df contains only numbers
    if df.isin([np.nan, np.inf, -np.inf]).any(1).any():
        raise Exception("LinDep: some cells don't contain numbers")

    # Find linearly dependent columns.
    # https://stackoverflow.com/questions/44555763/is-there-a-way-to-check-for-linearly-dependent-columns-in-a-dataframe
    _reduced_form, inds = sympy.Matrix(df.values).rref()

    # inds contains the indexes of independent columns.
    # Get the names of dependent columns.
    inds_set = set(inds)
    col_names = [df.columns[i] for i in range(len(df.columns)) if i not in inds_set]
    return col_names
