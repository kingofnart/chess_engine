#!/bin/bash

python app.py &
FLASK_PID=$!

sleep 5

pytest -vv

exit_code=$?

kill $FLASK_PID
wait $FLASK_PID

exit $exit_code