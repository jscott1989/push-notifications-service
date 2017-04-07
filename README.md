Push Notifications Service
===
This is a Python solution to the MyBBC "Push Notification Service" challenge.

It is implemented using the Falcon API Framework, and can be run with any WSGI server.

Routes
===
POST /v1/users
-- Register a new user

GET /v1/users
-- List registered users

GET /v1/users/{username}
-- Get registered user information

GET /v1/users/{username}/notifications
-- Get the number of sent notifications

POST /v1/users/{username}/notifications
-- Send a notification

Requirements
====
Python3 and pip

Instructions
====
Install requirements with ``pip install -r requirements.txt``

Run the server from this directory with ``gunicorn push_notifications.server:api`` (or with any other WSGI server).
Run tests with ``python -m unittest discover test``.