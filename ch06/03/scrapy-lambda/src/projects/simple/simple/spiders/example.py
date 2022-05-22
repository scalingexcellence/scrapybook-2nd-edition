import scrapy

# {
#   "project": "simple",
#   "args": [
#     "scrapy",
#     "crawl",
#     "example",
#     "-L",
#     "INFO"
#   ]
# }
class ExampleSpider(scrapy.Spider):
    name = 'example'
    allowed_domains = ['example.com']
    start_urls = ['http://example.com/']

    def parse(self, response):
        return {"url": response.url,
                "body": response.body.decode('utf8')}
