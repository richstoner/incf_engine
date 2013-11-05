from flask import render_template

from app import app, config
from routes import __all__

_pyflakes = __all__  # to pass pyflakes


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(port=config.get('PORT', 8000),
            debug=config.get('DEBUG', False))
