#!/bin/bash

# Start the API Gateway in the background
cd /app/api_gateway
sh bin/run.sh root/conf.yaml &

# Wait for the API Gateway to become healthy before starting the tickler
echo "Waiting for API Gateway to become healthy..."
while ! /usr/local/bin/healthcheck.sh > /dev/null 2>&1; do
  echo "API Gateway not ready yet, waiting..."
  sleep 2
done

echo "API Gateway is healthy, starting tickler..."
/app/tickler.sh &

# Wait for the API Gateway process to keep container alive
wait