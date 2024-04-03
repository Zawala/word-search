from unittest.mock import patch, MagicMock
import time
from server import textServicer, text_pb2_grpc, text_pb2
from server import search_file_jelly
import jellyfish

# Mock the jellyfish.jaro_winkler_similarity function to control its output
@patch('jellyfish.jaro_winkler_similarity', return_value=1.0)
def test_search_file_jelly_success(mock_jaro_winkler_similarity):
    # Simulate a file object with a single line
    # Simulate a file object with a single line
    file_content = "This is a test line.\n"
    file = MagicMock()
    file.__iter__.return_value = file_content.splitlines()

    # Call the function with the mocked file and a search term
    result = search_file_jelly(file, "test line")

    # Assert that the function returned the expected result
    assert result == "String Found"
    # Assert that the jellyfish.jaro_winkler_similarity function was called with the correct arguments
    mock_jaro_winkler_similarity.assert_called_once_with("This is a test line.", "test line")


@patch('jellyfish.jaro_winkler_similarity', return_value=0.9)
def test_search_file_jelly_not_found(mock_jaro_winkler_similarity):
    # Simulate a file object with a single line
    file_content = "This is a test line.\n"
    file = MagicMock()
    file.__iter__.return_value = file_content.splitlines()

    # Call the function with the mocked file and a search term
    result = search_file_jelly(file, "test line", threshold=1.0)

    # Assert that the function returned the expected result
    assert result == "STRING NOT FOUND"
    # Assert that the jellyfish.jaro_winkler_similarity function was called with the correct arguments
    mock_jaro_winkler_similarity.assert_called_once_with("This is a test line.", "test line")


# Test for a string that is too long
def test_search_file_jelly_string_too_long():
    # Simulate a file object with a single line
    file_content = "This is a test line.\n"
    file = MagicMock()
    file.__iter__.return_value = file_content.splitlines()

    # Call the function with a search term that is too long
    result = search_file_jelly(file, "a" * 1025)

    # Assert that the function returned the expected result
    assert result == "String Too Long."


@patch('server.search_file_jelly', return_value="String Found")
def test_textServicer_search_success(mock_search_file_jelly):
    # Create a mock context object
    context = MagicMock()
    context.peer.return_value = "127.0.0.1"

    # Create a mock query_str object
    query_str = MagicMock()
    query_str.search_string = "test query"

    # Create an instance of textServicer
    servicer = textServicer()

    # Call the search method
    reply = servicer.search(query_str, context)

    # Assert that the search_file_jelly function was called with the correct arguments
    mock_search_file_jelly.assert_called_once()
    # Assert that the reply contains the expected information
    assert reply.info == "String Found"


# Test for the case where reread_onquery is False
@patch('server.search_file_jelly', return_value="String Found")
def test_textServicer_search_no_reread(mock_search_file_jelly):
    # Set reread_onquery to False
    reread_onquery = False

    # Create a mock context object
    context = MagicMock()
    context.peer.return_value = "127.0.0.1"

    # Create a mock query_str object
    query_str = MagicMock()
    query_str.search_string = "test query"

    # Create an instance of textServicer
    servicer = textServicer()

    # Call the search method
    reply = servicer.search(query_str, context)

    # Assert that the search_file_jelly function was called with the correct arguments
    mock_search_file_jelly.assert_called_once()
    # Assert that the reply contains the expected information
    assert reply.info == "String Found"
