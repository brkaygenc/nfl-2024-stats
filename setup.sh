mkdir -p ~/.streamlit/

echo "\
[general]\n\
email = \"\"\n\
" > ~/.streamlit/credentials.toml

echo "\
[server]\n\
port = $PORT\n\
address = \"0.0.0.0\"\n\
enableCORS = false\n\
enableXsrfProtection = false\n\
" > ~/.streamlit/config.toml 