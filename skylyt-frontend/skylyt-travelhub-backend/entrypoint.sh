#!/bin/bash
chown -R app:app /app/storage 2>/dev/null || true
exec gosu app "$@"
