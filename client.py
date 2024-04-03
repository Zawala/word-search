import logging
from databank import text_pb2_grpc, text_pb2
import grpc
import os
import sys
from typing import Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
    )


def _load_credential_from_file(filepath: str) -> bytes:
    """
    Load credentials from a file.

    Parameters:
    - filepath (str): The path to the file containing the credentials.

    Returns:
    - bytes: The loaded credentials.
    """
    real_path = os.path.join(os.path.dirname(__file__), filepath)
    with open(real_path, "rb") as f:
        return f.read()


ROOT_CERTIFICATE = _load_credential_from_file("credentials/ca-cert.pem")
CLIENT_CERTIFICATE_KEY = _load_credential_from_file(
    "credentials/client-key.pem")
CLIENT_CERTIFICATE = _load_credential_from_file("credentials/client-cert.pem")


# use created stub to trigger rpc
def send_rpc(stub: text_pb2_grpc.textStub, 
             search_string: str) -> Union[str, grpc.RpcError]:
    """
    Send an RPC request to the server and log the response.

    Parameters:
    - stub (text_pb2_grpc.textStub): The gRPC stub to use for sending the
      request.
    - search_string (str): The search string to include in the request.

    Returns:
    - Union[str, grpc.RpcError]: The response from the server or an RpcError
      if an error occurred.
    """
    # Create a request with a search string
    request = text_pb2.request(search_string=search_string)
    try:
        # Send the request to the server and receive the response
        response = stub.search(request)
        logging.info(response)
    except grpc.RpcError as rpc_error:
        # Log any errors encountered during the RPC call
        logging.error("Received error: %s", rpc_error)
        return rpc_error
    else:
        # Log the received message
        logging.info("Received message: %s", response)
        return response


# create secure grpc cahnnel
def secure_channel_request(search_string: str):
    """
    Create a secure gRPC channel and send a search request.

    This function creates a secure gRPC channel using SSL/TLS credentials,
      creates a stub
    to use the gRPC service, and sends a search request to the server.

    Parameters:
    - search_string (str): The search string to include in the request.

    Returns:
    - None
    """
    # Create SSL channel credentials using the provided certificates
    channel_credential = grpc.ssl_channel_credentials(
        ROOT_CERTIFICATE,
        CLIENT_CERTIFICATE_KEY,
        CLIENT_CERTIFICATE)
    # Create a secure channel to the server
    with grpc.secure_channel(
        '0.0.0.0:55000', channel_credential
    ) as channel:
        # Create a stub (client-side proxy) to use the gRPC service
        stub = text_pb2_grpc.textStub(channel)
        # Send the RPC request using the stub
        send_rpc(stub, search_string)


def insecure_channel_request(search_string: str):
  
    """
    Create an insecure gRPC channel and send a search request.

    This function creates an insecure gRPC channel, creates a stub to
      use the gRPC service,
    and sends a search request to the server.

    Parameters:
    - search_string (str): The search string to include in the request.

    Returns:
    - None
    """
    with grpc.insecure_channel(
        '0.0.0.0:55000'
    ) as channel:
        stub = text_pb2_grpc.textStub(channel)
        send_rpc(stub, search_string)


# Entry point of the script
if __name__ == "__main__":
    """
    Entry point of the script.

    This script prompts the user to choose between a secure or
      insecure connection to the server
    and sends a search request based on the user's input.
    """
    try:
        secure = input("Do you wish to connect via SSL? yN")
        if secure.lower() == 'y':
            secure_channel_request(sys.argv[1])
        elif secure.lower() == 'n':
            insecure_channel_request(sys.argv[1])
        else:
            logging.error("Invalid Selection")
    except Exception as e:
        logging.error(f"Error occurred: {e}")
