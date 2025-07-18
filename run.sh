#!/usr/bin/with-contenv bashio

bashio::log.info "Starting Entity Manager..."
bashio::log.warning "⚠️ ALPHA VERSION - This add-on is in early development!"
bashio::log.warning "⚠️ Use at your own risk - Not recommended for production!"

# Set environment variables
export HA_URL="http://supervisor/core"
export HA_TOKEN="${SUPERVISOR_TOKEN}"

# Get log level from configuration with fallback to info
LOG_LEVEL=$(bashio::config 'log_level' || echo 'info')
export LOG_LEVEL

bashio::log.info "Starting web UI with log level: ${LOG_LEVEL}"

# Change to app directory
cd /app || exit 1

# Start the Flask application
exec python3 web_ui.py
