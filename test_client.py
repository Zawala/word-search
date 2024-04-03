import unittest
from unittest.mock import MagicMock, patch
from client import send_rpc
from databank import text_pb2_grpc, text_pb2


class TestClient(unittest.TestCase):
    def test_send_rpc_success(self):
        # Mock the gRPC stub
        stub = MagicMock()
        # Define a search string to use in the test
        search_string = 'g9uH85RY'
        # Mock the search method of the stub to return a predefined response
        stub.search.return_value = text_pb2.reply(info="String Found")

        # Call the function with the mocked stub and the search string
        response = send_rpc(stub, search_string)

        # Assert the expected response
        self.assertEqual(response.info, "String Found")
        # Assert that the stub's search method was called with the correct arguments


if __name__ == '__main__':
    unittest.main()
