# -*- coding: utf-8 -*-
from base.base_request import Message, BaseRequest, BaseResponse


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
        "title": "The CompareResponse Schema",
        "required": [],  # write the fields which must be in response
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


class CrowdRealtimeAnalysisConfig(Message):
    y = "y"  # int32  6
    x = "x"  # int32  6
    density_map_config = "density_map_config"  # bool  3
    roi = "roi"  # RealtimeAnalysisOutputConfig  4


class RealtimeAnalysisOutputConfig(Message):
    min_interval = "min_interval"  # int32  2


class AnotherClass(Message):
    enable = "enable"  # bool  1
