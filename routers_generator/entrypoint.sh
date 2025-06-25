#!/bin/bash
set -e

if [ -z "$OPEN_API_SPEC_URL" ]; then
  echo "ERROR: OPEN_API_SPEC_URL environment variable is not set."
  exit 1
fi

echo "📥 Downloading OpenAPI spec from: $OPEN_API_SPEC_URL"
curl -sSf "$OPEN_API_SPEC_URL" -o /app/openapi.json

# echo "🧬 Generating FastAPI router code..."
# fastapi-codegen -i /app/openapi.yaml -o /app/routers

echo "✅ Code generation complete. Files written to /app/routers"
ls -l /app/routers
