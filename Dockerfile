ARG BUILD_FROM
FROM $BUILD_FROM

# Install requirements for add-on
RUN apk add --no-cache \
    python3 \
    py3-pip \
    py3-setuptools \
    py3-wheel \
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

# Create startup script
RUN echo '#!/usr/bin/env bashio' > /run.sh && \
    echo 'bashio::log.info "Starting Entity Manager..."' >> /run.sh && \
    echo 'bashio::log.warning "⚠️ ALPHA VERSION - This add-on is in early development!"' >> /run.sh && \
    echo 'bashio::log.warning "⚠️ Use at your own risk - Not recommended for production!"' >> /run.sh && \
    echo 'export HA_URL="http://supervisor/core"' >> /run.sh && \
    echo 'export HA_TOKEN="${SUPERVISOR_TOKEN}"' >> /run.sh && \
    echo 'exec python3 web_ui.py' >> /run.sh && \
    chmod a+x /run.sh

CMD [ "/run.sh" ]