
import ssl
def make_mtls_server_ctx(server_cert, server_key, client_ca):
    ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ctx.verify_mode = ssl.CERT_REQUIRED
    ctx.load_cert_chain(certfile=server_cert, keyfile=server_key)
    ctx.load_verify_locations(cafile=client_ca)
    return ctx
def make_mtls_client_ctx(client_cert, client_key, server_ca):
    ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=server_ca)
    ctx.load_cert_chain(certfile=client_cert, keyfile=client_key)
    return ctx
