import os
from io import StringIO
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
def find_lindep_csv(csv_text, job_id):
    """
    Celery task to process text from .csv file.
    """
    update_job_status(job_id, JS_RUNNING)
    try:
        result = find_lindep_csv_int(csv_text)

    except Exception as e:
        print(f'job #{job_id} error: {e}')
        update_job_status(job_id, JS_ERROR, result=str(e))

    else:
        update_job_status(job_id, JS_DONE, json.dumps(result))
        print(f"job #{job_id} complete: {' '.join(result)}")


def find_lindep_csv_int(csv_text):
    """
    Process text from .csv file - find linearly dependent columns.
    """
    df = pd.read_csv(StringIO(csv_text))

    # Expected file format:
    # "","col0","col1",...,"colN"
    # "2020-04-13 00:00:00+00:00","0.9166","0.0022",...,"0.6983"
    # "2020-04-13 01:00:00+00:00","0.1147","0.0912",...,"0.3672"
    # ...

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
