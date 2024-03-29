import scrapy


class ExampleSpider(scrapy.Spider):
    name = 'example'
    allowed_domains = ['example.com']
    start_urls = ['http://example.com/']

    def parse(self, response):
        yield {"url": response.url,
               "body": response.body.decode('utf8')[:40]}
