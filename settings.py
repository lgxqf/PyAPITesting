from base.api_type import APIType

project_root = 'PyAPITesting'
remote_port = 22

HOST = {"host": "0.0.0.0"}
HOST = {"host": "172.20.25.106"}

TEST_ENV = {
    "172.20.25.106": {
        APIType.public: ":30443",
        APIType.internal: ":30999/api"},
}
