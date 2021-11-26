#!/bin/bash

# See: Safer bash scripts with 'set -euxo pipefail':
# https://vaneyckt.io/posts/safer_bash_scripts_with_set_euxo_pipefail/
# https://coderwall.com/p/fkfaqq/safer-bash-scripts-with-set-euxo-pipefail
set -e           # Exit immediately if a command exits with a non-zero status
set -u           # Treat unset variables as an error when substituting
set -o pipefail  # Stop pipeline (with non-zero exit code) on error in the middle


# Quote here-doc delimiter (EOSQL) to prevent variable expansion on here-doc lines.
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-"EOSQL"
    create database lindep;
EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname lindep <<-"EOSQL"
    create table jobs (
        id serial,
        status text not null,
        result text,

        primary key (id)
    );
EOSQL
