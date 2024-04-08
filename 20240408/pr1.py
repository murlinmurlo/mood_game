def rest_example():
    """
    REST API Example
    =================

    This is an example of a REST API implementation in Python.

    API Endpoints
    -------------

    **GET /users**
        Get a list of all users.

    **GET /users/{id}**
        Get details of a specific user.

    **POST /users**
        Create a new user.

    **PUT /users/{id}**
        Update details of a specific user.

    **DELETE /users/{id}**
        Delete a specific user.

    Usage
    -----

    To use this API, make HTTP requests to the appropriate endpoints.

    Example:

    .. code-block:: http

        GET /users HTTP/1.1
        Host: example.com

    Response:

    .. code-block:: json

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            "users": [
                {
                    "id": 1,
                    "name": "John Doe",
                    "email": "john@example.com"
                },
                {
                    "id": 2,
                    "name": "Jane Smith",
                    "email": "jane@example.com"
                }
            ]
        }
    """

    # Your API implementation goes here
    pass

# Call the function to see the formatted reST output
print(rest_example.__doc__)
