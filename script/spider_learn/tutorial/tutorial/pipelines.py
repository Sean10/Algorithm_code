# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem
from scrapy import Request
import hashlib


class CustomImagePipeline(ImagesPipeline):
    # def process_item(self, item, spider):
        # return item

    def get_media_requests(self, item, info):
        # for src in item['src']:
        #     print(f"get_media_requests: {item['src']}")
        #     yield Request(url=item['src'], )

        urls = ItemAdapter(item).get(self.images_urls_field, [])
        return [Request(u, meta={"item": item}) for u in urls]


    def item_completed(self, results, item, info):
        # def x(item_new):
        #     # item_new = request.meta['item']
        #     image_guid = item_new['src'].split('/')[-1]
        #     path = f"{item_new['name']}/{image_guid}.jpg"
        #     return path
        print(results)
        image_paths = [y for ok, y in results if ok]

        if not image_paths:
            raise DropItem("Item contains no images")
        # item['image_paths'] = image_paths
        return item

    def file_path(self, request, response=None, info=None):
        item_new = request.meta['item']

        def x(prefix, url):
            # item_new = request.meta['item']
            image_guid = url.split('/')[-1]
            path = f"{prefix}/{image_guid}"
            return path

        image_paths = [x(item_new['name'], y) for y in item_new['src']]
        # item_new = request.meta['item']
        # image_guid = item_new['src'].split('/')[-1]
        # path = f"{item_new['name']}/{image_guid}.jpg"
        print(f"path: {image_paths}")
        return image_paths[0]
