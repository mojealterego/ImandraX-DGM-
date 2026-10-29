"""Live localhost TLS 1.3 handshake test; not a production deployment claim."""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import ssl
import threading
import time
from urllib.error import URLError
from urllib.request import urlopen

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
import pytest

import imandrax_dgm.approval_api as api
from imandrax_dgm.rsi import RSIReviewStore


def _self_signed(tmp_path):
    key=rsa.generate_private_key(public_exponent=65537,key_size=2048)
    subject=x509.Name([x509.NameAttribute(NameOID.COMMON_NAME,'localhost')])
    now=datetime.now(timezone.utc)
    cert=(x509.CertificateBuilder().subject_name(subject).issuer_name(subject)
          .public_key(key.public_key()).serial_number(x509.random_serial_number())
          .not_valid_before(now-timedelta(days=1)).not_valid_after(now+timedelta(days=1))
          .add_extension(x509.SubjectAlternativeName([x509.DNSName('localhost')]),critical=False)
          .sign(key,hashes.SHA256()))
    cert_path=tmp_path/'cert.pem';key_path=tmp_path/'key.pem'
    cert_path.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    key_path.write_bytes(key.private_bytes(serialization.Encoding.PEM,
                             serialization.PrivateFormat.TraditionalOpenSSL,
                             serialization.NoEncryption()))
    return cert_path,key_path


def test_real_authority_tls13_and_tls12_rejected(tmp_path,monkeypatch):
    cert,key=_self_signed(tmp_path)
    store=RSIReviewStore(tmp_path/'reviews.sqlite3')
    tokens={'proposer':'a'*40,'runner':'b'*40,'reviewer':'c'*40}
    captured={}
    real_build=api.build_server
    def capture_server(address,store,tokens):
        srv=real_build(address,store,tokens)
        captured['server']=srv
        return srv
    monkeypatch.setattr(api,'build_server',capture_server)
    thread=threading.Thread(target=api.serve_tls,args=(('127.0.0.1',0),store,tokens),
        kwargs={'certfile':str(cert),'keyfile':str(key)},daemon=True)
    thread.start()
    try:
        for _ in range(100):
            if 'server' in captured and isinstance(captured['server'].socket,ssl.SSLSocket):
                break
            time.sleep(.02)
        else:
            pytest.fail('TLS server did not initialize')
        port=captured['server'].server_port
        url=f'https://127.0.0.1:{port}/healthz'
        context=ssl._create_unverified_context()  # test-only self-signed certificate
        context.minimum_version=ssl.TLSVersion.TLSv1_3
        with urlopen(url,context=context,timeout=3) as response:
            assert response.status==200
            assert response.read().startswith(b'{"status":"up"')
        old=ssl._create_unverified_context()
        old.maximum_version=ssl.TLSVersion.TLSv1_2
        with pytest.raises((URLError,ssl.SSLError,ConnectionError,OSError)):
            urlopen(url,context=old,timeout=3)
    finally:
        if 'server' in captured:
            captured['server'].shutdown()
            captured['server'].server_close()
        thread.join(timeout=3)
