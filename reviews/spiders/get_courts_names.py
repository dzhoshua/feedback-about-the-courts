import scrapy

class GetCourtsNamesSpider(scrapy.Spider):
    name = "get_courts_names"
    allowed_domains = ["sudrf.ru"]
    start_urls = ["https://sudrf.ru/index.php?id=300&act=go_search&searchtype=fs&court_name=&court_subj=0&court_type=RS&court_okrug=0"]

    def parse(self, response):
        # сбор названий
        for court in response.css("ul.search-results li"):
            
            yield {
                "name": court.css("a.court-result::text").get(),
                # "email": court.css("div.courtInfoCont a::text").get()
            }
