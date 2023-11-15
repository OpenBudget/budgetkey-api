import os

enable_mock_oauth = (os.environ.get("ENABLE_MOCK_OAUTH") == "1")
db_connection_string = os.environ.get('DATABASE_PRIVATE_URL')
