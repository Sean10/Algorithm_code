


## 待办
* 导出基本数据
* 导出思维导图(以文本格式, 最好是markdown)
* 导出待办
* 以文件形式导出内容, 最好是markdown的压缩包
	* [一个zip，打包全部：前端JSZip多文件流下载压缩新姿势 \- ByteZoneX社区](https://www.bytezonex.com/archives/KhEQldsV.html)
	* 浏览器导入库 https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.0/jszip.min.js



# changelog

### 20240610
* js格式提取出对应的标题和内容
	* snippet取前缀作为标题一部分
	* 以创建时间戳作为标题
* 文件形式存储笔记
	* 支持使用`JSZip`和`FileSaver`导出文本格式输出笔记

### 20240529
* 分析完毕2条基本的todo待办数据获取接口, 实现基本的采集出待办文字