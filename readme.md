# Text search

This document outlines the steps to set up and run a Python-based text search application, which includes a server and a client for searching through large text files. The application utilizes gRPC for communication and secure communication channels.

## Prerequisites

- Python 3.8 or higher installed on your system.
- Access to the terminal or command line interface.

## Setup

1. **Initialize a Virtual Environment**:
   ```
   ```

2. **Activate the Virtual Environment**:
   ```
   source python3/bin/activate
   ```

3. **Install Dependencies**:
   Navigate to the project directory and run the following command to install the required packages:
   ```
   pip3 install -r files/requirements.txt
   ```

## Running the Server

1. **Start the Server**:
   Execute the following command to start the server:
   ```
   python serve.py
   ```
   Ensure all certificates are in place for the server to start successfully.

## Running the Client

1. **Search for Strings**:
   To search for a specific string in the file, run the client script with the search parameter as an argument. For example:
   ```
   python client.py 'g9uH85RY'
   ```

## Running the Server as a Linux Service

1. **Copy the Service File**:
   Copy the `Rinne_lookup.service` file to `/etc/systemd/system/`:
   ```
   sudo cp Rinne_lookup.service /etc/systemd/system/
   ```

2. **Reload Daemons**:
   ```
   sudo systemctl daemon-reload
   ```

3. **Enable the Service**:
   ```
   sudo systemctl enable Rinne_lookup.service
   ```

4. **Start the Service**:
   ```
   sudo systemctl start Rinne_lookup.service
   ```

5. **Check the Service Status**:
   ```
   sudo systemctl status Rinne_lookup.service
   ```

**Note**: Ensure the service file points to the absolute location of the binary file in the Linux system.

These steps should be sufficient to set up and run the text search application.