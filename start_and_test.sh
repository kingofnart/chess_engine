#!/bin/bash

python app.py &

sleep 5

pytest -vv

exit_code=$?

wait

exit $exit_code