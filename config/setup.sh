#!/bin/bash

# Make the script executable
chmod +x config/setup.sh

# Export environment variables
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Install dependencies
pip install -r requirements.txt

# Set Streamlit configuration
mkdir -p ~/.streamlit
echo "[server]
headless = true
port = $PORT
enableCORS = true
" > ~/.streamlit/config.toml

echo "[theme]
primaryColor='#F63366'
backgroundColor='#0E1117'
secondaryBackgroundColor='#262730'
textColor='#FAFAFA'
font='sans serif'
" >> ~/.streamlit/config.toml 