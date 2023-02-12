import scrapy

class BlogSpider(scrapy.Spider):
    name = 'blogspider'
    # start_urls = ['https://t66y.com/thread0806.php?fid=8&type=4']

    def start_requests(self):
        urls = [
            'https://t66y.com/thread0806.php?fid=8&search=&type=4&page=1',
            'https://t66y.com/thread0806.php?fid=8&search=&type=4&page=2',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        
        for title in response.css('title'):
            yield {'title': title.css('::text').get()}

        for next_page in response.css('a.next'):
            yield response.follow(next_page, self.parse)



