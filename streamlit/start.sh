#!/bin/bash

# Extract SSL certs from env vars if present (using Python for robust newline handling)
if [ ! -z "$SSL_CERT_PEM" ] && [ ! -z "$SSL_KEY_PEM" ]; then
    echo "Extracting SSL certificates from environment variables..."
    python -c "
import os

def normalize_pem(pem_str):
    if not pem_str: return ''
    # Replace literal \n with actual newline character
    content = pem_str.replace('\\\\n', '\\n').replace('\\\\r', '')
    
    # Ensure proper separation of headers/footers
    content = content.replace('-----BEGIN CERTIFICATE-----', '-----BEGIN CERTIFICATE-----\\n')
    content = content.replace('-----END CERTIFICATE-----', '\\n-----END CERTIFICATE-----')
    
    content = content.replace('-----BEGIN PRIVATE KEY-----', '-----BEGIN PRIVATE KEY-----\\n')
    content = content.replace('-----END PRIVATE KEY-----', '\\n-----END PRIVATE KEY-----')
    content = content.replace('-----BEGIN RSA PRIVATE KEY-----', '-----BEGIN RSA PRIVATE KEY-----\\n')
    content = content.replace('-----END RSA PRIVATE KEY-----', '\\n-----END RSA PRIVATE KEY-----')
    
    # Clean up potential double newlines
    while '\\n\\n' in content:
        content = content.replace('\\n\\n', '\\n')
        
    return content.strip() + '\\n'

cert = os.environ.get('SSL_CERT_PEM')
key = os.environ.get('SSL_KEY_PEM')

if cert:
    with open('cert.pem', 'w') as f:
        f.write(normalize_pem(cert))
if key:
    with open('key.pem', 'w') as f:
        f.write(normalize_pem(key))
"
fi

# Fallback: Generate self-signed certificate if not exists
if [ ! -f cert.pem ]; then
    echo "Generating self-signed certificate..."
    openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
fi

echo "Starting ESET Agent UI on port 8501 (HTTPS)..."
streamlit run src/main.py --server.port 8501 --server.address 0.0.0.0 --server.sslCertFile=cert.pem --server.sslKeyFile=key.pem
