#!/bin/bash

# Print environment variables for debugging
echo "POSTGRES_DB: $POSTGRES_DB"
echo "POSTGRES_USER: $POSTGRES_USER"
echo "POSTGRES_PASSWORD: $POSTGRES_PASSWORD"
echo "DATABASE_URL: $DATABASE_URL"
echo "CHESS_DB_SECRET_KEY: $CHESS_DB_SECRET_KEY"

python app.py &
FLASK_PID=$!

sleep 5

pytest -x -vv

exit_code=$?

kill $FLASK_PID
wait $FLASK_PID

exit $exit_code