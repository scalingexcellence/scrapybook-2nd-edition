BOT_NAME = 'quotes'

SPIDER_MODULES = ['quotes.spiders']
NEWSPIDER_MODULE = 'quotes.spiders'

ROBOTSTXT_OBEY = True

EXTENSIONS = {
    'scrapy_demo_cloudwatch_log.DemoLogger': 100
}
