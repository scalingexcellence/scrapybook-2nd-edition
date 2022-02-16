# -*- coding: utf-8 -*-
import scrapy

from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, MapCompose


class CoinLoader(ItemLoader):
    default_item_class = dict
    default_output_processor = TakeFirst()


class AllcoinsSpider(scrapy.Spider):
    name = 'allcoins'
    allowed_domains = ['coinmarketcap.com']
    start_urls = ['https://coinmarketcap.com/all/views/all/']

    def parse(self, response):

        to_full_url = MapCompose(response.urljoin)
        to_float = MapCompose(float)

        for row in response.css('table tr')[1:]:
            l = CoinLoader(selector=row)
            l.add_css('name', 'td.currency-name::attr(data-sort)')
            l.add_css('url', 'td.currency-name a::attr(href)', to_full_url)
            l.add_css('symbol', 'td.col-symbol::text')
            l.add_css('market_cap', 'td.market-cap::attr(data-sort)', to_float)
            l.add_css('circulating_supply',
                      'td.circulating-supply::attr(data-sort)',
                      to_float)
            l.add_css('price_usd', 'a.price::attr(data-usd)', to_float)
            l.add_css('price_btc', 'a.price::attr(data-btc)', to_float)
            yield l.load_item()
