import scrapy
import xml.etree.ElementTree as ET
from ..items import TutorialItem, ImageItem

class BlogSpider(scrapy.Spider):
    name = 'link'
    # start_urls = ['https://t66y.com/thread0806.php?fid=8&type=4']

    def start_requests(self):
        domain = "somthing"
        urls = [
            f'https://{domain}/thread0806.php?fid=8&search=&type=4&page=1',
            'https://{domain}/thread0806.php?fid=8&search=&type=4&page=2',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):

        # for title in response.css('title'):
        #     yield {'title': title.css('::text').get()}

        for next_page in response.xpath('//*[@id="tbody"]/tr/td/h3/a').extract():
            item = TutorialItem()
            html = ET.fromstring(next_page)
            item['name'] = html.text
            path = html.attrib['href']

            item['link'] = response.urljoin(path)
            keyword = "something"
            if keyword not in item['name']:
                continue
            print(item['name'], item['link'])

            yield scrapy.Request(item['link'], callback=self.parse_image, cb_kwargs={"name": item['name']})
            # yield response.follow(next_page, self.parse)


    def parse_image(self, response, name):

        src_list = response.xpath('//*[@id="conttpc"]/img/@ess-data').extract()
        # with open("xxx.html", "wb") as f :
        #     f.write(response.body)
        for src in src_list:
            # print(src)

            item = ImageItem()
            item['name'] = name
            item['src'] = [src]
            yield item



