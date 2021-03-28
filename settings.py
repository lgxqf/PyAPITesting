from base.api_type import APIType

project_root = 'PyAPITesting'
remote_port = 22

HOST = {"host": "127.0.0.1"}

TEST_ENV = {
    "172.20.25.106": {
        APIType.public: ":30443",
        APIType.internal: ":30888/api"},
}
