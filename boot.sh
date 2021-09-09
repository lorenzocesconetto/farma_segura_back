#!/bin/bash
scrapyrt -s TIMEOUT_LIMIT=15000 &
while true; do
  flask deploy
  if [[ "$?" == "0" ]]; then
    break
  fi
  echo "Deploy command failed, retrying in 10 secs..."
  sleep 10
done
exec gunicorn -b :5000 --workers 5 --threads 1 --access-logfile - --error-logfile - main:app
