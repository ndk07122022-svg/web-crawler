#!/bin/sh
# Start Vite preview server with Railway's PORT
PORT=${PORT:-5173}
exec npm run preview -- --host 0.0.0.0 --port $PORT
