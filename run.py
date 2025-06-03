from app import create_app
from config import config
import os
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.middleware.proxy_fix import ProxyFix

# Create application instance
app = create_app(config['default'])

# Security headers middleware
Talisman(
    app,
    force_https=app.config.get('FORCE_HTTPS', False),
    strict_transport_security=app.config.get('STRICT_TRANSPORT_SECURITY', True),
    session_cookie_secure=app.config.get('SESSION_COOKIE_SECURE', True),
    content_security_policy=app.config['SECURE_HEADERS']['Content-Security-Policy'],
    content_security_policy_nonce_in=['script-src']
)

# Rate limiting
limiter = Limiter(
    app,
    key_func=get_remote_address,
    storage_uri=app.config['RATELIMIT_STORAGE_URI'],
    strategy=app.config['RATELIMIT_STRATEGY'],
    default_limits=[app.config['RATELIMIT_DEFAULT']]
)

# Proxy fix (if behind reverse proxy)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Theme endpoint
@app.route('/set-theme', methods=['POST'])
def set_theme():
    theme = request.json.get('theme', 'dark')
    if theme in ['dark', 'light', 'red', 'blue', 'green']:
        session['theme'] = theme
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error', 'message': 'Invalid theme'}), 400

if __name__ == '__main__':
    # Run in development mode
    app.run(host='0.0.0.0', port=5000, debug=True)
else:
    # Run in production mode with gunicorn
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
