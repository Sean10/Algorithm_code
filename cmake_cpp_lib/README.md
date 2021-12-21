任何其他程序，想用libXXX.a，链接时都需要链接libXXX.a所依赖的动态库

cmake里自动进行了这个链接关系的处理, 所以链二进制时, 不需要再人工指定静态库所链的动态库了


这种库之间的链式依赖, 动态库包含静态库, 可以编译通过. 

如果想要全是动态库, 那就难了. 目前来看, 无解.

通过nm查看.o文件的内容, 可以发现linux平台确实可以 .所以初步怀疑是这套代码在mac上运行的问题.

确认, 在mac上用容器重新跑就正常了
# dynamic_link



# static_link


# Reference
1. [CaptainBlackboard/D\#0001\.md at master · Captain1986/CaptainBlackboard](https://github.com/Captain1986/CaptainBlackboard/blob/master/D%230001-undefined_reference_to_XXX/D%230001.md)