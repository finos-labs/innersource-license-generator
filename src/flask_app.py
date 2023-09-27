import io
import os
from logging.config import dictConfig
from flask import Flask, render_template, request, send_file, session
from license_generator import generate_license_text, check_missing_fields, sanitize_input


dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})


def setup_app(app):
    app.config.update(PERMANENT_SESSION_LIFETIME=600,
                      SESSION_COOKIE_SECURE=True,
                      SESSION_COOKIE_HTTPONLY=True,
                      SESSION_COOKIE_SAMESITE='Lax',
                      )


app = Flask(__name__)
app.secret_key = os.urandom(24)
setup_app(app)


@app.after_request
def apply_caching(response):
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "form-action 'self'"
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.set_cookie('username', 'flask', secure=True, httponly=True, samesite='Lax')
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/generate_license', methods=['POST'])
def generate_license():
    form_data = sanitize_input(request.form)  # Sanitize input data
    app.logger.info('Sanitized inputs: %s', form_data)
    missing_fields = check_missing_fields(form_data)  # Validate input data
    if missing_fields:
        app.logger.error('Missing fields: %s', missing_fields)
        return render_template('error.html', message=f'Invalid form data, missing fields: {missing_fields}')

    license_text, human_readable_license = generate_license_text(form_data)
    session['form_data'] = form_data
    clauses_text = human_readable_license

    return render_template('result.html', clauses_text=clauses_text, license_text=license_text)


@app.route('/download')
def download_text_file():

    form_data = session.get('form_data', 'no data found')
    content, human_readable_text = generate_license_text(form_data) 
    filename = "License.md"

    # Create an in-memory file-like object
    file_obj = io.BytesIO()
    file_obj.write(content.encode('utf-8'))
    file_obj.seek(0)  # Move the file position to the beginning

    return send_file(
        file_obj,
        mimetype='text/plain',
        as_attachment=True,
        download_name=filename
    )


#@app.route('/download_license')
def download_license():
    return send_file('license.pdf', as_attachment=True, download_name='license.pdf')


if __name__ == '__main__':
    debug = True if os.getenv('DEBUG_FLASK') else False  # set environment variable to explicitly allow debug
    app.run(debug=debug)
