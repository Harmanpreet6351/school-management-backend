#!/bin/bash

# Check if APP_PATH and SCRIPTS_PATH environment variables exist
if [ -z "$MOUNT_PATH" ] || [ -z "$SCRIPTS_PATH" ]; then
    echo "Error: MOUNT_PATH or SCRIPTS_PATH environment variable is missing."
    echo "MOUNT_PATH and SCRIPTS_PATH must be set before running this script."
    exit 1
fi

# sleep for 5 seconds and wait for DB to initialiize properly
sleep 5s

# upgrade migrations
alembic upgrade head

# Check if HIVE_ENV is set to "dev"
if [ "$SCHOOL_ENVIRONMENT" == "dev" ]; then
    echo "Running FastAPI in development mode..."
    fastapi dev $MOUNT_PATH/app/main.py --host 0.0.0.0
else
    echo "Running FastAPI in production mode..."
    fastapi run $APP_PATH/app/main.py
fi
