## 基于Python的接口自动化测试框架，简单、易用

## 主要功能

### 1.根据ProtoBuf文件直接生成Python测试接口， 生成内容包括 
* 接口对应的request和response类 request_response.py
* 接口的调用方法 api_service.py
* 接口的名字列表 api_config.py
* 支持嵌套Message

### 2.自动对Response做检验
* 根据pb定义 校验各字段的类型
* 针对数值字段 如果pb中定义了validator 则根据validator生成检验规则， 如：
  - int32 limit = 3 [(validator.field) = {int_gt: 0, int_lt: 10000}];

## 要求
- 仅支持Protobuf3,且proto文件要提前做好格式化
- Protobuf中定义的request必须名字以Request结尾: XXXRequest
- Protobuf中定义的response必须名字以Response结尾: XXXResponse

## TODO
- 每个Response支持生成到单独的文件
-  分析 validator[(validator.field) = {length_gt: 0}];
   [(validator.field) = {int_gt: 0, int_lt: 10000}];
- 支持 pb Oneof关键字分析   
- 测试 AnalysisConfigRequest


## 参考文档
- http://json-schema.org/
- JSON Schema入门 https://www.jianshu.com/p/1711f2f24dcf?utm_campaign=hugo
- Golang ProtoBuf Validator Compiler https://github.com/mwitkow/go-proto-validators/

