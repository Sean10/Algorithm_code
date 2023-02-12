import scrapy
from ..items import ImageItem

class MeiSpider(scrapy.Spider):
    name = "image"
    # allowed_domains = ["t66y.com"]
    allowed_domains = ["www.lmmbtc.com", 'img.flmfxz.com']
    # 迫于好像是js加载的, 用这个方案暂时忽略
    # start_urls = ["https://t66y.com/htm_data/2302/8/5541041.html"]
    start_urls = ["https://www.lmmbtc.com/1038825.html"]
    
    def parse(self, response):
        src_list = response.xpath('//*[@id="post-1038825"]/div/div/p/img/@src').extract()

        for src in src_list:
            print(src)

            item = ImageItem()
            item['name'] = "1"
            item['src'] = [src]
            yield item
