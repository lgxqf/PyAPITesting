from base.api_type import APIType

project_root = 'PyAPITesting'
remote_port = 22

HOST = {"host": "0.0.0.0"}

test_env = {
    "0.0.0.0": {
        APIType.public: ":30020",
        APIType.internal: ":30999/api"},
}
