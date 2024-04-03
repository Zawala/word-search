import logging
from databank import text_pb2_grpc, text_pb2
from concurrent import futures
import time
import io
import grpc
import os
import configparser
from fuzzywuzzy import fuzz
from typing import Union, IO

# Configure logging
logging.basicConfig(
    level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s'
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


# Load configuration from a file
config = configparser.ConfigParser()
config.read('files/config.cfg')
search_file_path = config.get('DEFAULT', 'linuxpath')
log_file_path = config.get('DEFAULT', 'log_file')
connection_port = config.get('DEFAULT', 'connection_port')
reread_onquery = config.get('DEFAULT', 'REREAD_ON_QUERY')
ssl_security = config.get('DEFAULT', 'ssl_security')
reread_onquery = reread_onquery.lower() in ('true', '1', 'yes')
secure_server = ssl_security.lower() in ('true', '1', 'yes')
SERVER_CERTIFICATE = _load_credential_from_file("credentials/server-cert.pem")
SERVER_CERTIFICATE_KEY = _load_credential_from_file(
    "credentials/server-key.pem")
ROOT_CERTIFICATE = _load_credential_from_file("credentials/ca-cert.pem")


# Load the search file content if not reloading on query
if reread_onquery is False:
    with open(search_file_path, 'r') as file:
        global_file_content = file.read()


# Function to perform fuzzy search on a file
def search_file_fuzzy(file: Union[IO[str], IO[bytes]],
                      search_term: str, threshold: float = 1.0) -> str:
    """
    Perform a fuzzy search on a file using the Jaro-Winkler similarity
    algorithm.

    Parameters:
    - file (Union[IO[str], IO[bytes]]): The file or file-like object to search
    in.

    - search_term (str): The search term to look for in the file.
    - threshold (float, optional): The minimum similarity score for a match
    to be considered. Defaults to 1.0.

    Returns:
    - str: A message indicating whether the string was found or not.
    """
    matches = []
    search_term = search_term.strip()
    start_time = time.time()

    # Check if the search term is too long

    if len(search_term) > 1024:
        logging.error(f'String Too Long: {search_term}')
        return "String Too Long."

    # Iterate over each line in the file
    for line_number, line in enumerate(file, start=1):
        # Perform fuzzy matching on each string
        score = fuzz.ratio(line.strip(), search_term) / 100.0
        if score >= threshold:
            # If a match is found, append the original line to the matches list
            matches.append((line_number, line.strip()))
            break
    if len(matches) == 0:
        end_time = time.time()
        execution_time = end_time - start_time
        logging.debug(f"DEBUG: Execution time: {execution_time} seconds")
        return "STRING NOT FOUND"
    else:
        end_time = time.time()
        execution_time = end_time - start_time
        logging.debug(f"DEBUG: Execution time: {execution_time} seconds")
        for match in matches:
            logging.info(f"Line {match[0]}")
            return "String Found"


# gRPC service class
class textServicer(text_pb2_grpc.textServicer):
    """
    A gRPC service class for handling text search queries.

    This class implements the search method to process search queries,
      log the query,
    and return the search results based on the query string. It supports
      both reloading
    the search file on each query and using a global file content for
      efficiency.
    """

    def search(self, query_str, context):
        """
        Process a search query and return the search results.

        This method logs the search query and the requesting IP address, then
          performs
        a fuzzy search on the specified file or global file content based on
          the query string.
        The search results are encapsulated in a reply object and returned to
          the client.

        Parameters:
        - query_str (text_pb2.Query): The search query object containing the
          search string.
        - context (grpc.ServicerContext): The gRPC context object, providing
          information about the request.

        Returns:
        - text_pb2.reply: A reply object containing the search results or a
          message indicating the search outcome.
        """
        # Log the search query
        reply = text_pb2.reply()
        logging.debug(f"DEBUG: Search query: {query_str}")
        logging.debug(f"DEBUG: Requesting IP: {context.peer()}")
        if reread_onquery:
            with open(search_file_path, 'r') as file:
                reply.info = search_file_fuzzy(file, query_str.search_string)
                return reply
        else:
            reply.info = search_file_fuzzy(
                io.StringIO(global_file_content), query_str.search_string)
            return reply


def start_secure_server():
    """
    Start a secure gRPC server with SSL/TLS credentials.

    This function initializes a gRPC server with a thread pool executor,
      adds the textServicer
    class to the server for handling text search queries, configures the
      server with SSL/TLS
    credentials, and starts listening on a specified port for secure
      connections.

    The server is configured to use the SSL/TLS credentials specified in the
      SERVER_CERTIFICATE_KEY
    and SERVER_CERTIFICATE variables, which are loaded from the credentials
      directory.

    Parameters:
    - None

    Returns:
    - grpc.Server: The initialized and started gRPC server instance.
    """
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=100), )
    # Add the defined class to the server
    text_pb2_grpc.add_textServicer_to_server(
            textServicer(), server)
    # Listen on port in config
    server_credentials = grpc.ssl_server_credentials(
        (
            (
                SERVER_CERTIFICATE_KEY,
                SERVER_CERTIFICATE,
            ),
        )
    )
    logging.info(f'Starting secure server, port {connection_port}.')
    server.add_secure_port(f'0.0.0.0:{connection_port}', server_credentials)
    return server


def start_insecure_server():
    """
    Start an insecure gRPC server.

    This function initializes a gRPC server with a thread pool executor, adds 
    the textServicer
    class to the server for handling text search queries, and starts listening
      on a specified port
    for insecure connections.

    Parameters:
    - None

    Returns:
    - grpc.Server: The initialized and started gRPC server instance.
    """
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=100), )
    # Add the defined class to the server
    text_pb2_grpc.add_textServicer_to_server(
            textServicer(), server)
    # Listen on port in config
    logging.info(f'Starting insecure server, port {connection_port}.')
    server.add_insecure_port(f'0.0.0.0:{connection_port}')
    return server


def serve():
    """
    Start the gRPC server based on the configuration and keep it running
      indefinitely.

    This function checks the configuration to determine whether to start a
    secure or insecure gRPC server.
    It then starts the server and enters a sleep-loop to keep the server
      running indefinitely.
    The server can be stopped by a KeyboardInterrupt (Ctrl+C), at which point
      it will be gracefully shut down.

    Parameters:
    - None

    Returns:
    - None
    """
    if secure_server:
        server = start_secure_server()
    else:
        server = start_insecure_server()
    try:
        server.start()
        # Keep the server alive with a sleep-loop
        try:
            while True:
                time.sleep(86400)
        except KeyboardInterrupt:
            server.stop(0)
    except Exception as e:
        logging.error(f'An Error occurred: {e}')


# Entry point of the script
if __name__ == '__main__':
    serve()
