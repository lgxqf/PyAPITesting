## 基于Python的接口自动化测试框架，简单、易用

## 主要功能

### 根据ProtoBuf(.proto), Swagger(.json)文件自动生成Python测试接口， 生成内容包括

* 接口对应的request和response类 request_response.py
* 接口的调用方法 api_service.py
* 接口的名字列表 api_config.py
* Proto支持嵌套Message
* 根据proto定义 校验各字段的类型


## 要求
### Proto
- 仅支持Protobuf3,且proto文件要提前做好格式化
- Protobuf中定义的request必须名字以Request结尾: XXXRequest
- Protobuf中定义的response必须名字以Response结尾: XXXResponse
- oneof关键字会生成单独的类 需要额外手动处理, 生成的类会以RENAME_IT开头

### Swagger
- 仅支持工具导出的swagger文件 

## TODO

* 每个Response支持生成到单独的文件
* 针对数值字段 如果pb中定义了validator 则根据validator生成检验规则， 
- 如： int32 limit = 3 [(validator.field) = {int_gt: 0, int_lt: 10000}];
- 支持的validator关键字：
  - 数值：int_gt，int_lt,float_gt,float_lt,float_epsilon,float_gte,float_gle
  - 字符：length_gt,length_lt,length_eq

## 参考文档

- http://json-schema.org/
- JSON Schema入门 https://www.jianshu.com/p/1711f2f24dcf?utm_campaign=hugo
- Golang ProtoBuf Validator Compiler https://github.com/mwitkow/go-proto-validators/
- Go Validator https://github.com/mwitkow/go-proto-validators/blob/master/validator.proto


## CMD
pip install pipreqs  
pipreqs ./ --encoding=utf8 --force
pip install  -r requirement.txt