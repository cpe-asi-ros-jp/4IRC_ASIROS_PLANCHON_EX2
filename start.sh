#!/usr/bin/env bash
(trap 'kill 0' SIGINT; \
    python3 services/camera.py 2>&1 | sed 's/^/[CAMERA SERVICE]: /' & \
    python3 app.py 2>&1 | sed 's/^/[SERVER]: /')