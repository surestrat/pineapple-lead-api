#!/bin/sh
# wait-for-postgres.sh

set -e

host="$1"
user="$2"
shift 2
cmd="$@"

# Extract password from DATABASE_URL environment variable
if [[ $DATABASE_URL =~ ://[^:]+:([^@]+)@ ]]; then
  POSTGRES_PASSWORD="${BASH_REMATCH[1]}"
else
  echo "Could not extract password from DATABASE_URL"
  POSTGRES_PASSWORD=""
fi

# Try to connect to the database
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$host" -U "$user" -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - executing command"
exec $cmd
