#!/bin/sh
# This script performs a health check for the API Gateway service.
# It checks if the API Gateway is reachable and returns a valid JSON response.

# Environment variables like GATEWAY_INTERNAL_BASE_URL, GATEWAY_PORT, and GATEWAY_TEST_ENDPOINT
# are automatically available in the container's healthcheck execution environment.
URL="${GATEWAY_INTERNAL_BASE_URL}:${GATEWAY_PORT}${GATEWAY_TEST_ENDPOINT}"

echo "Attempting to check API Gateway health at: $URL"

# Use curl to get the HTTP status code and save the response body to a temporary file.
# -s: Silent mode (don't show progress meter or error messages)
# -k: Allow insecure server connections when using SSL (useful for local development with self-signed certs)
# -w "%{http_code}": Output only the HTTP status code
# -o /tmp/api_response.json: Write the response body to this file
STATUS=$(curl -sk -w "%{http_code}" -o /tmp/api_response.json "$URL")

# Check if the HTTP status code is not 401 (Unauthorized).
# The API Gateway might return 401 if no authentication token is provided,
# but a successful health check should indicate the service is up and responding.
if [ "$STATUS" -ne 401 ]; then
  # Check if the response body contains a JSON object (indicated by a '{' character).
  # This is a basic check to ensure the response is not empty or malformed.
  if grep -q "{" /tmp/api_response.json; then
    echo "API Gateway healthcheck successful: HTTP status $STATUS, response contains JSON."
    exit 0 # Exit with 0 for success
  else
    echo "API Gateway healthcheck failed: Response does not contain a JSON object."
    exit 1 # Exit with 1 for failure
  fi
else
  echo "API Gateway healthcheck failed: Received HTTP status $STATUS (expected non-401)."
  exit 1 # Exit with 1 for failure
fi
