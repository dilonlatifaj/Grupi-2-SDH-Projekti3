import socket
import hmac
import hashlib
import logging
import json
import os

_raw_secret = os.environ.get("HMAC_SECRET", "")
if not _raw_secret:
    raise EnvironmentError(
        "HMAC_SECRET environment variable is not set. "
        "Set it before starting the server:\n"
        "  export HMAC_SECRET='your_strong_secret_key_here'"
    )
SECRET_KEY: bytes = _raw_secret.encode("utf-8")

HOST: str = "127.0.0.1"
PORT: int = 65432
BUFFER_SIZE: int = 4096

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - SERVER - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def verify_hmac(message: str, received_hmac: str) -> bool:
    expected_hmac = hmac.new(
        SECRET_KEY,
        message.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected_hmac, received_hmac)

def handle_client(conn: socket.socket, addr: tuple) -> None:

    logger.info("Connection established with %s:%s", *addr)
