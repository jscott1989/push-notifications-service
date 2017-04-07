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

Assumptions
====
From the instructions it appears you want the notification to be sent to all devices associated
with a given access token. This is what I have implemented.

I have also only implemented the functionality requested in the document. The API supports
user registration, listing all users, user lookup, and sending notifications. I haven't
implemented support for modifying users once they are registered. I also have not implemented
pagination on the list of users. This may be required depending on the expected use of the API.


Design Decisions
====
The data is stored in a dictionary abstracted away behind an InMemoryStorage class. This is injected
into the server, so if this was needed to run on multiple servers it could be replaced with
a database-backed implementation.

Due to the GIL the dictionary as a whole is thread-safe, though I had to use a lock to ensure the register and increment functionality would be safe.

I put everything under /v1 as some form of versioning APIs is good practice and this was the simplest
to implement for this task.

Requirements
====
Python3 and pip

Instructions
====
Install requirements with ``pip install -r requirements.txt``

Run the server from this directory with ``gunicorn push_notifications.server:api`` (or with any other WSGI server).
Run tests with ``python -m unittest discover test``.