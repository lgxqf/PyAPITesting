# -*- coding: utf-8 -*-
from base.base_request import BaseRequest, BaseResponse


class ErrorMsg(object):
    invalid_account = 'name is invalid'
    invalid_password = 'password is wrong'


class AuthorizationRequest(BaseRequest):
    account = 'account'
    password = 'password'

    def get_request(self):
        return {
            self.account: {
                'valid': 'a',
                'invalid': [("", ErrorMsg.invalid_account), (None, ErrorMsg.invalid_account)],
            },
            self.password: {
                'valid': 'ad',
                'invalid': [("", ErrorMsg.invalid_password), (None, ErrorMsg.invalid_password)],
            }
        }


class AuthorizationResponse(BaseResponse):
    """
    {
        "result"：{"token":"abcd"}
    }
    """
    schema = {
        "type": "object",
        "title": "The Authorization Schema",
        "required": [
            "result"
        ],
        "properties": {
            "result": {
                "type": "object",
                "required": [
                    "token",
                ],
                "properties": {
                    "token": {
                        "type": "string",
                        "pattern": "^(.*)$"
                    }
                }
            }
        }
    }
