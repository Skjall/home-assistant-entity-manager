#!/usr/bin/with-contenv bashio

# Configure logging
LOG_LEVEL=$(bashio::config 'log_level' || echo 'info')

bashio::log.info "Starting Entity Manager..."
bashio::log.warning "⚠️ ALPHA VERSION - This add-on is in early development!"
bashio::log.warning "⚠️ Use at your own risk - Not recommended for production!"

# Start the Flask application
cd /app
exec python3 web_ui.py
