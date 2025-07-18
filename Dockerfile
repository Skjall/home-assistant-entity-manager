ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base-python:3.13-alpine3.20
FROM $BUILD_FROM

# Install build dependencies
# Note: Python is already installed in the base image
RUN apk add --no-cache \
    gcc \
    musl-dev \
    python3-dev

# Copy requirements file
COPY requirements.txt /tmp/

# Install Python dependencies
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# Copy application files
COPY web_ui.py /app/
COPY dependency_scanner.py /app/
COPY dependency_updater.py /app/
COPY device_registry.py /app/
COPY entity_registry.py /app/
COPY entity_restructurer.py /app/
COPY ha_client.py /app/
COPY ha_websocket.py /app/
COPY label_registry.py /app/
COPY naming_overrides.py /app/
COPY scene_updater.py /app/
COPY templates/ /app/templates/
WORKDIR /app

# Copy optional naming_overrides.json if it exists
RUN echo '{}' > /app/naming_overrides.json

# Create s6-overlay service directory
RUN mkdir -p /etc/services.d/entity-manager

# Copy s6-overlay startup script
COPY run.sh /etc/services.d/entity-manager/run
RUN chmod a+x /etc/services.d/entity-manager/run

# Copy finish script for proper cleanup
COPY finish.sh /etc/services.d/entity-manager/finish
RUN chmod a+x /etc/services.d/entity-manager/finish