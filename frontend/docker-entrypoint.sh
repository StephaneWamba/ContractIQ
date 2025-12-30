#!/bin/sh
set -e

# Install dependencies if node_modules doesn't exist or is empty
if [ ! -d "node_modules" ] || [ -z "$(ls -A node_modules 2>/dev/null)" ]; then
  echo "Installing dependencies..."
  pnpm install
fi

# Run the original command
exec "$@"


