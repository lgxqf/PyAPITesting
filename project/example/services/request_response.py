# -*- coding: utf-8 -*-
from base.base_request import Message, BaseRequest, BaseResponse


class AnalysisConfigRequest(BaseRequest):
    age = "age"  # int32  1 [(validator.field) {int_gt: 0, int_lt: 100}]
    name = "name"  # string  2 [(validator.field) {regex:"^[a-z0-9\\-]+$", length_eq: 50}]
    map_config = "map_config"  # bool  3
    time = "time"  # RealtimeConfig  4
    map = "map"  # MapConfig  5

    def get_request(self):
        return {
            self.age: {
                # int32
                'valid': '',
                'invalid': []
            },
            self.name: {
                # string
                'valid': '',
                'invalid': []
            },
            self.map_config: {
                # bool
                'valid': '',
                'invalid': []
            },
            self.time: {
                # RealtimeConfig
                'valid': '',
                'invalid': []
            },
            self.map: {
                # MapConfig
                'valid': '',
                'invalid': []
            },
        }


class RealtimeConfig(Message):
    min_interval = "min_interval"  # int32  1


class MapConfig(Message):
    size = "size"  # int32  1


class RENAME_IT_location(Message):
    latitude = "latitude"  # int32  6
    longitude = "longitude"  # int32  7


class AuthorizationRequest(BaseRequest):
    account = "account"  # string  1 [(validator.field) {regex:"^[a-zA-Z0-9_\\-\\.]+$", length_gt: 3, length_lt: 21}]
    password = "password"  # string  2 [(validator.field) {regex:"^[a-zA-Z0-9]+$",length_gt: 5, length_lt: 19}]

    def get_request(self):
        return {
            self.account: {
                # string
                'valid': '',
                'invalid': []
            },
            self.password: {
                # string
                'valid': '',
                'invalid': []
            },
        }


class AuthorizationResponse(BaseResponse):
    token = "token"  # string  1
    schema = {
        "type": "object",
        "title": "The AuthorizationResponse Schema",
        "required": [],  # write the fields which must be in response
        "properties": {
            "token": {
                "type": "string",
            },
        }
    }


class EmptyRequest(BaseRequest):

    def get_request(self):
        return {
        }


class EmptyResponse(BaseResponse):
    schema = {
        "type": "object",
        "title": "The EmptyResponse Schema",
        "required": [],  # write the fields which must be in response
        "properties": {
        }
    }


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
    score_desc = "score_desc"  # bytes  2
    personnel_kind = "personnel_kind"  # string  3
    is_hit = "is_hit"  # bool  4
    hit_score = "hit_score"  # float  5
    similar_score = "similar_score"  # double  6
    count = "count"  # int32  7


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
                'invalid': []
            },
            self.captured_time: {
                # google.protobuf.Timestamp
                'valid': '',
                'invalid': []
            },
            self.image: {
                # bytes
                'valid': '',
                'invalid': []
            },
            self.image_id: {
                # string
                'valid': '',
                'invalid': []
            },
            self.liveness_image: {
                # bytes
                'valid': '',
                'invalid': []
            },
            self.image_url: {
                # string
                'valid': '',
                'invalid': []
            },
            self.face_id: {
                # string
                'valid': '',
                'invalid': []
            },
            self.personnel: {
                # Personnel
                'valid': '',
                'invalid': []
            },
            self.status: {
                # Status
                'valid': '',
                'invalid': []
            },
            self.name: {
                # repeated string
                'valid': [],
                'invalid': []
            },
        }


class CompareResponse(BaseResponse):
    image_id = "image_id"  # string  1 [(validator.field) {length_lt: 256}]
    score_desc = "score_desc"  # bytes  2
    personnel_kind = "personnel_kind"  # string  3
    is_hit = "is_hit"  # bool  4
    hit_score = "hit_score"  # float  5
    similar_score = "similar_score"  # double  6
    count = "count"  # int32  7
    result = "result"  # repeated Result  8
    schema = {
        "type": "object",
        "title": "The CompareResponse Schema",
        "required": [],  # write the fields which must be in response
        "properties": {
            "image_id": {
                "type": "string",
            },
            "score_desc": {
                "type": "string",  # bytes
            },
            "personnel_kind": {
                "type": "string",
            },
            "is_hit": {
                "type": "boolean",  # bool
            },
            "hit_score": {
                "type": "number",  # float
            },
            "similar_score": {
                "type": "number",  # double
            },
            "count": {
                "type": "integer",  # int32
            },
            "result": {
                "type": "array",  # Result
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
