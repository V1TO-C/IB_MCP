#!/bin/sh
# This script performs a health check for the Tickler service.
# It checks if the TICKLE_BASE_URL and TICKLE_ENDPOINT are reachable and return a non-401 status.

# Environment variables like TICKLE_BASE_URL and TICKLE_ENDPOINT
# are automatically available in the container's healthcheck execution environment.
URL="${TICKLE_BASE_URL}${TICKLE_ENDPOINT}"

echo "Attempting to check Tickler health at: $URL"

# Use curl to get the HTTP status code.
# -s: Silent mode (don't show progress meter or error messages)
# -k: Allow insecure server connections (useful for local development with self-signed certs)
# -o /dev/null: Discard response body, we only care about the status code
# -w "%{http_code}": Output only the HTTP status code to stdout
STATUS=$(curl -sk -o /dev/null -w "%{http_code}" "$URL")

# Check if the HTTP status code is not 401 (Unauthorized).
# A non-401 status indicates the service is up and responding as expected.
if [ "$STATUS" -ne 401 ]; then
  echo "Tickler healthcheck successful: HTTP status $STATUS."
  exit 0 # Exit with 0 for success
else
  echo "Tickler healthcheck failed: Received HTTP status $STATUS (expected non-401)."
  exit 1 # Exit with 1 for failure
fi
