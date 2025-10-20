#!/bin/sh

set -e

cd /app; exec /usr/local/bin/python /app/main.py "$@"
