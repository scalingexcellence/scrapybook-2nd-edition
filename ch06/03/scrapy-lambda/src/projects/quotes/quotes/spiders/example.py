import scrapy

# {
#   "project": "quotes",
#   "args": [
#     "scrapy",
#     "crawl",
#     "example",
#     "-L",
#     "INFO",
#     "-a",
#     "category=inspirational",
#     "-o",
#     "s3://<FIXME: destination bucket>/%(name)s-inspirational-%(time)s.jl:jl"
#   ]
# }
class ExampleSpider(scrapy.Spider):
    name = 'example'
    
    def start_requests(self):
        yield scrapy.Request(f'https://quotes.toscrape.com/tag/{self.category}')

    def parse(self, response):
        return {"url": response.url,
                "body": response.body.decode('utf8')}
