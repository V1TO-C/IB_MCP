#!/bin/sh
# This script performs a health check for the API Gateway service.
# It checks if the API Gateway is reachable and responding.

# Debug: Print environment variables
echo "DEBUG: GATEWAY_SERVER_BASE_URL=${GATEWAY_SERVER_BASE_URL}"
echo "DEBUG: GATEWAY_PORT=${GATEWAY_PORT}"
echo "DEBUG: GATEWAY_TEST_ENDPOINT=${GATEWAY_TEST_ENDPOINT}"

# For healthcheck, we need to check the LOCAL gateway running in THIS container
# Use GATEWAY_INTERNAL_BASE_URL for internal checks (usually http://localhost or http://127.0.0.1)
URL="${GATEWAY_SERVER_BASE_URL}:${GATEWAY_PORT}${GATEWAY_TEST_ENDPOINT}"

echo "Attempting to check API Gateway health at: $URL"

# Use curl to check if the gateway is responding
# -s: Silent mode
# -k: Allow insecure server connections (self-signed certs)
# -m 5: Maximum time allowed for the transfer (5 seconds timeout)
# -o /dev/null: Discard response body
# -w "%{http_code}": Output only HTTP status code
# We don't use -f because we expect 401/403 before login which is still a valid response

HTTP_CODE=$(curl -sk -m 5 -o /dev/null -w "%{http_code}" "$URL" 2>/dev/null)
CURL_EXIT=$?

echo "DEBUG: curl exit code: $CURL_EXIT"
echo "DEBUG: HTTP response code: $HTTP_CODE"

# If curl succeeded in connecting (exit code 0, 22, or 28 are acceptable)
# Exit code 0 = success
# Exit code 22 = HTTP error (but connection worked)
# Exit code 28 = timeout (but connection attempted)
if [ $CURL_EXIT -eq 0 ]; then
  # Check if we got a valid HTTP response code
  if [ -n "$HTTP_CODE" ] && [ "$HTTP_CODE" -ge 100 ] 2>/dev/null && [ "$HTTP_CODE" -lt 600 ] 2>/dev/null; then
    echo "API Gateway healthcheck SUCCESSFUL: HTTP status $HTTP_CODE (service is responding)"
    exit 0
  fi
fi

echo "API Gateway healthcheck FAILED: curl exit code $CURL_EXIT, HTTP status: ${HTTP_CODE:-NONE}"
exit 1
