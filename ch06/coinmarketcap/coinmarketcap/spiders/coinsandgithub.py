# -*- coding: utf-8 -*-
import scrapy
import re
import json

from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, MapCompose
from w3lib.http import basic_auth_header


class CoinLoader(ItemLoader):
    default_item_class = dict
    default_output_processor = TakeFirst()


class CoinsandgithubSpider(scrapy.Spider):
    name = 'coinsandgithub'
    allowed_domains = ['coinmarketcap.com', 'api.github.com']
    start_urls = ['https://coinmarketcap.com/all/views/all/']

    def parse(self, response):

        to_full_url = MapCompose(response.urljoin)
        to_float = MapCompose(float)

        for row in response.css('table tr')[1:10]:
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
            item = l.load_item()
            yield response.follow(item['url'],
                                  callback=self.parse_coin_page,
                                  meta={"item": item})

    def parse_coin_page(self, response):
        item = response.meta["item"]
        css = 'span[title="Source Code"] + a::attr(href)'
        item['repo'] = response.css(css).extract_first()

        m = re.match('https://github.com/([^/]+)', item['repo'])
        if not m:
            return item

        item['user'] = m.group(1)
        url = ("https://api.github.com/users/{}/repos?sort=updated"
               .format(item['user']))
        return response.follow(url,
                               headers={'Authorization': basic_auth_header('lookfwd', 'Aer!de22')},
                               callback=self.parse_github_repos,
                               meta={"item": item})

    def parse_github_repos(self, response):
        item = response.meta["item"]
        repos = json.loads(response.body.decode('utf-8'))

        print([(repo['name'], repo['stargazers_count']) for repo in repos])

        max_stars = max(repo['stargazers_count'] for repo in repos)

        for repo in repos:
            if repo['stargazers_count'] == max_stars:
                item['maingit'] = repo['name']
                item['stars'] = repo['stargazers_count']
                item['watchers'] = repo['watchers_count']
                item['language'] = repo['language']
                item['forks'] = repo['forks_count']
                break

        url = ("https://api.github.com/repos/{}/{}/stats/commit_activity"
               .format(item['user'], item['maingit']))
        return response.follow(url,
                               headers={'Authorization': basic_auth_header('lookfwd', 'Aer!de22')},
                               callback=self.parse_github_commit_activity,
                               meta={"item": item})

    def parse_github_commit_activity(self, response):
        item = response.meta["item"]
        commit_activity = json.loads(response.body.decode('utf-8'))

        if response.status == 202:
            print("retry")
            return response.request.replace(dont_filter=True)

        activity = [day for week in commit_activity for day in week["days"]]
        activity = activity[:-7]  # Discard last week, not done yet
        average = lambda i: float(sum(i)) / max(len(i), 1)
        item['daily_commits_year'] = round(average(activity), 2)
        item['daily_commits_quarter'] = round(average(activity[:-90]), 2)
        item['daily_commits_month'] = round(average(activity[:-30]), 2)
        return item
