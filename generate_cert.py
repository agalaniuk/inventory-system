from OpenSSL import crypto

# Create a key pair
key = crypto.PKey()
key.generate_key(crypto.TYPE_RSA, 2048)

# Create a self-signed cert
cert = crypto.X509()
cert.get_subject().CN = "localhost"
cert.set_serial_number(1000)
cert.gmtime_adj_notBefore(0)
cert.gmtime_adj_notAfter(10 * 365 * 24 * 60 * 60)  # 10 years
cert.set_issuer(cert.get_subject())
cert.set_pubkey(key)
cert.sign(key, 'sha256')

# Save the cert and key
with open("cert.pem", "wt") as f:
    f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert).decode('utf-8'))
with open("key.pem", "wt") as f:
    f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key).decode('utf-8'))