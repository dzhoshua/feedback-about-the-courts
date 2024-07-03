import scrapy
from scrapy.crawler import CrawlerProcess

from reviews.spiders.get_courts_info import GetCourtsInfoSpider

process = CrawlerProcess(
    settings={
        "FEEDS": {
            "items.json": {"format": "json"},
        },
    }
)

process.crawl(GetCourtsInfoSpider)
process.start()  # the script will block here until the crawling is finished
