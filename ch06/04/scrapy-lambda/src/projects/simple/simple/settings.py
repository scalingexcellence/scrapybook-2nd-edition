BOT_NAME = 'simple'

SPIDER_MODULES = ['simple.spiders']
NEWSPIDER_MODULE = 'simple.spiders'

ROBOTSTXT_OBEY = True

import os
FEEDS = {
    f"s3://{os.environ['DESTINATION_BUCKET']}/%(name)s-%(time)s.jl": {
        'format': 'jsonlines'
    }
}
