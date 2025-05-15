# MRTOF Timing System

A simple webserver to control the MRTOF timing sequencer FPGA via TCP

This repository consists of three parts:

## Backend Server

Folder: APIServer

The backend server is responsible for:
1. Accepting duration information from user (via frontend server)
2. Calculate FPGA timings
3. Read and Write to the FPGA via TCP

NOTE: the server was developed with python 3.10 and uses the fastAPI library.

## Frontend Server

Folder: webserver

The frontend server is responsible for communicating user actions to the backend server

## Settings

Folder: settings:

All settings related files are to be stored here. Currently, it contains the duration parameters at KISS-MRTOF as of 2025-5-15.

## How to Run the System

1. To run the backend server, go into the APIServer directory and run: fastapi run apiserver.py
2. To run the frontend server, go into the webserver directory and run: python -m http.server
3. To access the timing system, open a browser and go to the IP address of the server.
