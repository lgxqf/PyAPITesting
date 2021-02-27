from base.base_request import Message, BaseRequest, BaseResponse


class AuthorizationRequest(BaseRequest):
    account = "account"  # string  1 [(validator.field) {regex:"^[a-zA-Z0-9_\\-\\.]+$", length_gt: 3, length_lt: 21}]
    password = "password"  # string  2 [(validator.field) {regex:"^[a-zA-Z0-9]+$",length_gt: 5, length_lt: 19}]

    def get_request(self):
        return {
            self.account: {
                # string
                'valid': '',
                'invalid': ''
            },
            self.password: {
                # string
                'valid': '',
                'invalid': ''
            },
        }


class AuthorizationResponse(BaseResponse):
    token = "token"  # string  1
    schema = {
        "type": "object",
        "properties": {
            "token": {
                "type": "string",
            },
        }
    }


class EmptyRequest(BaseRequest):
    pass


class EmptyResponse(BaseResponse):
    pass


class Personnel(Message):
    PERSONNEL_LEVEL_UNKNOWN = 0
    PERSONNEL_LEVEL_RED = 1
    PERSONNEL_LEVEL_ORANGE = 2
    PERSONNEL_LEVEL_YELLOW = 3


class Status(Message):
    STATUS_SEND = 0
    STATUS_UNSEND = 1


class Result(Message):
    key = "key"  # string  1
    score = "score"  # float  2
    personnel_kind = "personnel_kind"  # string  3
    is_hit = "is_hit"  # bool  4


class CompareRequest(BaseRequest):
    device_id = "device_id"  # string  1 [(validator.field) {regex:"^[0-9]+$", length_eq: 20}]
    captured_time = "captured_time"  # google.protobuf.Timestamp  2
    image = "image"  # bytes  3
    image_id = "image_id"  # string  4
    liveness_image = "liveness_image"  # bytes  5
    image_url = "image_url"  # string  6
    face_id = "face_id"  # string  7
    personnel = "personnel"  # Personnel  8
    status = "status"  # Status  9
    name = "name"  # repeated string  10

    def get_request(self):
        return {
            self.device_id: {
                # string
                'valid': '',
                'invalid': ''
            },
            self.captured_time: {
                # google.protobuf.Timestamp
                'valid': '',
                'invalid': ''
            },
            self.image: {
                # bytes
                'valid': '',
                'invalid': ''
            },
            self.image_id: {
                # string
                'valid': '',
                'invalid': ''
            },
            self.liveness_image: {
                # bytes
                'valid': '',
                'invalid': ''
            },
            self.image_url: {
                # string
                'valid': '',
                'invalid': ''
            },
            self.face_id: {
                # string
                'valid': '',
                'invalid': ''
            },
            self.personnel: {
                # Personnel
                'valid': '',
                'invalid': ''
            },
            self.status: {
                # Status
                'valid': '',
                'invalid': ''
            },
            self.name: {
                # repeated string
                'valid': [],
                'invalid': ''
            },
        }


class CompareResponse(BaseResponse):
    image_id = "image_id"  # string  1 [(validator.field) {length_lt: 256}]
    result = "result"  # repeated Result  2
    schema = {
        "type": "object",
        "properties": {
            "image_id": {
                "type": "string",
            },
            "result": {
                "type": "array",
                "items": [
                    {
                        "type": "object",  # Result
                    },
                ]
            },
        }
    }


class Info(Message):
    track_id = "track_id"  # string  1
    device_id = "device_id"  # string  2
    entity_id = "entity_id"  # string  3
    captured_time = "captured_time"  # google.protobuf.Timestamp  4
    image_url = "image_url"  # string  5
