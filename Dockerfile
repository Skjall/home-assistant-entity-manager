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

# Copy application
COPY . /app
WORKDIR /app

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