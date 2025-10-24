#!/bin/sh
# This script performs a health check for the API Gateway service.
# It checks if the API Gateway is reachable and responding.

# For healthcheck, we need to check the LOCAL gateway running in THIS container
# Before login, most endpoints return "Access Denied", so we just verify the service responds
URL="https://localhost:${GATEWAY_PORT}${GATEWAY_TEST_ENDPOINT}"

echo "Attempting to check API Gateway health at: $URL"

# Use curl to check if the gateway is responding
# -s: Silent mode
# -k: Allow insecure server connections (self-signed certs)
# -f: Fail silently on HTTP errors (will make curl return non-zero for 4xx/5xx)
# -m 5: Maximum time allowed for the transfer (5 seconds timeout)
# We don't use -f because we expect 401/403 before login

RESPONSE=$(curl -sk -m 5 -w "%{http_code}" -o /dev/null "$URL" 2>&1)
CURL_EXIT=$?

# If curl succeeded in connecting (exit code 0) or got a response (even error)
# then the gateway is running. Common codes: 200, 401, 403, 404
if [ $CURL_EXIT -eq 0 ] || [ -n "$RESPONSE" ]; then
  # Check if we got an HTTP response code (any response means gateway is running)
  if [ "$RESPONSE" -ge 100 ] 2>/dev/null && [ "$RESPONSE" -lt 600 ] 2>/dev/null; then
    echo "API Gateway healthcheck successful: HTTP status $RESPONSE (service is responding)"
    exit 0
  fi
fi

echo "API Gateway healthcheck failed: curl exit code $CURL_EXIT, HTTP status: $RESPONSE"
exit 1
