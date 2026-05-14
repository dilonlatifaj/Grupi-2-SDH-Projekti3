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

    with conn:
        while True:
            try:
                data = conn.recv(BUFFER_SIZE)
            except ConnectionResetError:
                logger.warning("Client %s:%s reset the connection.", *addr)
                break

            if not data:
                logger.info("Client %s:%s disconnected.", *addr)
                break
            try:
                payload = json.loads(data.decode("utf-8"))
                message: str = payload.get("message", "")
                received_hmac: str = payload.get("hmac", "")

                if not message or not received_hmac:
                    raise ValueError("Payload missing 'message' or 'hmac' field.")

            except (json.JSONDecodeError, UnicodeDecodeError):
                response = "Error: Invalid message format. Expected JSON with 'message' and 'hmac' fields."
                logger.warning("Received malformed data from %s:%s", *addr)
                conn.sendall(response.encode("utf-8"))
                continue

            except ValueError as exc:
                response = f"Error: {exc}"
                logger.warning("Incomplete payload from %s:%s — %s", *addr, exc)
                conn.sendall(response.encode("utf-8"))
                continue

            print(f"\nMessage received with HMAC: [{message} | {received_hmac}]")
            logger.info("Received message from %s:%s — validating HMAC...", *addr)
            print("Validating HMAC...")

            if verify_hmac(message, received_hmac):
                response = "Message verified successfully. Integrity and authenticity confirmed."
                print(response)
                logger.info("HMAC verification PASSED for message from %s:%s", *addr)
            else:
                response = "Error: Message verification failed! Integrity compromised."
                print(response)
                logger.warning("HMAC verification FAILED for message from %s:%s", *addr)

            try:
                conn.sendall(response.encode("utf-8"))
            except BrokenPipeError:
                logger.warning("Could not send response — client %s:%s already disconnected.", *addr)
                break

def start_server() -> None:
    """
    Bind to HOST:PORT and accept clients in a continuous loop.
    Each client is handled sequentially (single-threaded).
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((HOST, PORT))
        server_sock.listen()

        print("Server started and awaiting messages...")
        logger.info("Server listening on %s:%s", HOST, PORT)

        while True:
            try:
                conn, addr = server_sock.accept()
                handle_client(conn, addr)
            except KeyboardInterrupt:
                print("\nServer shutting down.")
                logger.info("Server stopped by user (KeyboardInterrupt).")
                break
            except Exception as exc:
                logger.error("Unexpected server error: %s", exc)


if __name__ == "__main__":
    start_server()
