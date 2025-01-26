import os
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple
from src.app import app as flask_app
import streamlit.web.bootstrap
import sys
from werkzeug.wrappers import Response

def run_streamlit():
    """Run the Streamlit application"""
    sys.argv = ["streamlit", "run", "src/streamlit_app.py"]
    return streamlit.web.bootstrap.run()

def create_app():
    """Create the WSGI application"""
    def streamlit_handler(environ, start_response):
        if environ['PATH_INFO'].startswith('/api/'):
            return flask_app(environ, start_response)
        return run_streamlit()(environ, start_response)

    return streamlit_handler

application = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    run_simple('0.0.0.0', port, application, use_reloader=True)
