## 基于Python的接口自动化测试框架，简单、易用

## 主要功能

### 根据Protobuf(.proto)文件直接生成Python测试接口， 生成内容包括 
    - request和response类 request_response.py
    - 接口的调用方法 api_service.py
    - 接口的字符列表 api_config.py

### 自动生成response对应的json schema 对返回类型做检查


## 要求
- Protobuf中定义的request必须名字以Request结尾: XXXRequest
- Protobuf中定义的response必须名字以Response结尾: XXXResponse

## TODO
-  分析 validator[(validator.field) = {length_gt: 0}];
   [(validator.field) = {int_gt: 0, int_lt: 10000}];
   
- 测试 EntityListRequest

## 参考文档
- http://json-schema.org/
- JSON Schema入门 https://www.jianshu.com/p/1711f2f24dcf?utm_campaign=hugo

