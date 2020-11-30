# docker-graphviz
Graphviz in an Alpine Linux container

# build
``` bash
docker build -t graphviz ./
```

# use
``` bash
docker run --rm -v $(PWD):/graphviz graphviz dot -Tpng -o out.png ceph之SafeTimer.dot
```

奇怪, 传入中文的文件名, 有时候一开始不存在文件时第一次生成的png会无法打开,第二次生成就是正确的了.


# Reference
[noahwilliamsson/docker\-graphviz at graphviz\-update](https://github.com/noahwilliamsson/docker-graphviz/tree/graphviz-update)