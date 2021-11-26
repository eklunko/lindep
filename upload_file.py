#!/usr/bin/env python3
"""
Upload files via http.
"""

import sys
import argparse
import requests


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

    parser.add_argument('uri', type=str,
                        metavar='<URI>',
                        help="""URI to upload.""")

    parser.add_argument('filepath', type=str,
                        metavar='<FILE>',
                        help="""Path to the file.""")

    args = parser.parse_args(argv)

    with open(args.filepath, 'rb') as f:
        resp = requests.post(args.uri, data=f)

    if resp.status_code == 200:
        print(resp.json())
    else:
        print(f"Error {resp.status_code}: {resp.reason}", file=sys.stderr)


if __name__ == '__main__':
    main()
