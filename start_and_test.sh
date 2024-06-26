#!/bin/bash

# Start the server
gunicorn -w 1 -b 0.0.0.0:8000 app:app --log-level debug &
sleep 3
GUNICORN_PID=$!
echo "Starting Gunicorn with PID $GUNICORN_PID"

# Wait for the server to start
for i in {1..10}; do
  response=$(curl -I $APP_URL/login 2>/dev/null | head -n 1 | cut -d$' ' -f2)
  if [ "$response" == "200" ]; then
    echo "Server running at $APP_URL/login"
    break
  else
    echo "Waiting for server to start... Attempt $i response: $response"
    sleep 3
  fi
done

# Add a manual curl check for better logging
echo "Checking $APP_URL/login manually:"
curl -v $APP_URL/login

# Run the tests
pytest -s -x -vv
exit_code=$?

# Stop the server
kill $GUNICORN_PID
wait $GUNICORN_PID

# Propogate the exit code
exit $exit_code