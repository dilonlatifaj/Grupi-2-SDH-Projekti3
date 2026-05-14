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

def start_client() -> None:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((HOST, PORT))
            logger.info("Connected to server %s:%s", HOST, PORT)

            while True:
                try:
                    user_msg = input("\nEnter your message (or 'exit' to quit): ").strip()
                except (EOFError, KeyboardInterrupt):
                    print("\nExiting.")
                    break

                if user_msg.lower() == "exit":
                    logger.info("User requested disconnect.")
                    break

                if not user_msg:
                    print("Message cannot be empty. Please try again.")
                    continue

                response = send_message(sock, user_msg)

                if response is None:
                    print("Connection to server lost. Exiting.")
                    break

                print(f"Server response: {response}")

                if response.startswith("Error:"):
                    logger.warning("Server reported an error — message may have been tampered with.")

    except ConnectionRefusedError:
        print(f"Error: Could not connect to the server at {HOST}:{PORT}.")
        print("Make sure the server is running before starting the client.")
        logger.error("Connection refused by %s:%s", HOST, PORT)

    except Exception as exc:
        logger.error("Unexpected client error: %s", exc)
        print(f"An unexpected error occurred: {exc}")


if __name__ == "__main__":
    start_client()