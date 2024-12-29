mkdir -p ~/.streamlit/

echo "\
[theme]\n\
primaryColor = \"#F63366\"\n\
backgroundColor = \"#0E1117\"\n\
secondaryBackgroundColor = \"#31333F\"\n\
textColor = \"#FAFAFA\"\n\
font = \"sans serif\"\n\
[server]\n\
port = $PORT\n\
address = \"0.0.0.0\"\n\
enableCORS = false\n\
" > ~/.streamlit/config.toml 