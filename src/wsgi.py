import os
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple
from src.app import app as flask_app
import streamlit.web.bootstrap
import sys

def run_streamlit():
    sys.argv = ["streamlit", "run", "src/streamlit_app.py"]
    streamlit.web.bootstrap.run()

# Create the dispatcher middleware
application = DispatcherMiddleware(
    flask_app,  # Our Flask app handles everything under /api
    {
        "/": run_streamlit  # Streamlit handles the root path
    }
)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    run_simple('0.0.0.0', port, application, use_reloader=True)
