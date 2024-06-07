#!/bin/bash

python init_db.py
python app.py &
FLASK_PID=$!

sleep 5

pytest -x -vv

exit_code=$?

kill $FLASK_PID
wait $FLASK_PID

exit $exit_code