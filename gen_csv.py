#!/usr/bin/env python3
"""
Generate csv data for LinDep.
"""

import sys
import argparse
from datetime import datetime, timedelta
import csv

import numpy as np
import pandas as pd


PROGRAM_VERSION = '0.1.0'


def main(argv=None):
    "Main function."
    program_description = __doc__

    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(
        description=program_description, epilog=None,
        formatter_class=argparse.RawDescriptionHelpFormatter, add_help=False)

    parser.add_argument('--version', action='version',
                        version=PROGRAM_VERSION)

    parser.add_argument('--help', action='help', default=argparse.SUPPRESS,
                        help="Show this help message and exit.")

    parser.add_argument('-r', '--rows', type=int, default=10,
                        metavar='<rows>',
                        help="""Number of data rows.""")

    parser.add_argument('-c', '--columns', type=int, default=5,
                        metavar='<columns>',
                        help="""Number of data columns.""")

    parser.add_argument('-d', '--dup', type=int, default=0,
                        metavar='<N>',
                        help="""Replace last N columns values with the first column values.""")

    parser.add_argument('--prec', type=int, default=None,
                        metavar='<precision>',
                        help="""Precision for float numbers.""")

    args = parser.parse_args(argv)
    rows, cols, dups = args.rows, args.columns, args.dup
    if dups > cols - 1:
        print(f'Error: too big value for the --dup option')
        sys.exit(1)

    data = np.random.random(size=(rows, cols - dups))
    for _ in range(dups):
        data = np.hstack((data, data[:, :1]))

    # Get the midnight of the current UTC date
    t0 = datetime(*(datetime.utcnow().timetuple()[:3]))
    times = [t0 + timedelta(seconds=i) for i in range(rows)]

    df1 = pd.DataFrame(columns=['time'])
    df1.time = [t.isoformat(sep=' ') + '+00:00' for t in times]

    col_names = [f'col{i}' for i in range(cols)]
    df2 = pd.DataFrame(data, columns=col_names)

    # Stack two dataframes horizontally
    df = pd.concat([df1, df2], axis=1)

    float_format = f'%.{args.prec}f' if args.prec is not None else None
    csv_text = df.to_csv(index=False, float_format=float_format, quoting=csv.QUOTE_ALL)
    for s in csv_text.splitlines():
        print(s)


if __name__ == '__main__':
    main()
