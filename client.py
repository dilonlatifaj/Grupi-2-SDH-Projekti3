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
        "Set it before starting the client:\n"
        "  export HMAC_SECRET='your_strong_secret_key_here'"
    )
SECRET_KEY: bytes = _raw_secret.encode("utf-8")

HOST: str = "127.0.0.1"
PORT: int = 65432
BUFFER_SIZE: int = 4096

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - CLIENT - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def generate_hmac(message: str) -> str:

    return hmac.new(
        SECRET_KEY,
        message.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

def send_message(sock: socket.socket, message: str) -> str | None:

    msg_hmac = generate_hmac(message)
    logger.info("HMAC generated for message.")

    payload = json.dumps({"message": message, "hmac": msg_hmac})

    print(f"Sending message with HMAC: [{message} | {msg_hmac}]")
    logger.info("Transmitting message and HMAC to server.")
    sock.sendall(payload.encode("utf-8"))

    try:
        data = sock.recv(BUFFER_SIZE)
    except ConnectionResetError:
        logger.error("Server reset the connection while waiting for a response.")
        return None

    if not data:
        logger.warning("Server closed the connection without sending a response.")
        return None

    response = data.decode("utf-8")
    logger.info("Received server response: %s", response)
    return response