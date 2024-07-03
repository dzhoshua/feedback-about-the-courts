import scrapy
#from pathlib import Path
import time
import json


class GetCourtsInfoSpider(scrapy.Spider):
    name = "get_courts_info"
    allowed_domains = ["yandex.ru"]
    start_urls = ["https://yandex.ru/maps/"]


    def start_requests(self):

        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={"proxy": "http://1c8cc108f81a3ae2349ddcf47ae22d1ba5563f2a:@proxy.zenrows.com:8001"}
            )

    def parse(self, response):
        # считываем названия судов
        try:
            path = 'reviews/data/courts_names_emails.json'
            with open(path, 'r', encoding='utf-8') as f:
                courts_names = json.load(f)
        except FileNotFoundError:
            yield f"No such file or directory: '{path}'"

        #names = ["Иркутский районный суд Иркутской области"]#[courts_names[0]["name"]]
        if courts_names is not None:
             # проходимся по каждому суду
            for court in courts_names:
                 name = court['name']
                 time.sleep(2.5)

                 # ищем суд через поиск
                 yield scrapy.FormRequest.from_response(
		        response,
		        formdata={"text": name},
		        callback=self.follow_court_page,
		        meta={"proxy": "http://1c8cc108f81a3ae2349ddcf47ae22d1ba5563f2a:@proxy.zenrows.com:8001"}
		    )


    def follow_court_page(self, response):
        court_page = response.css("a.card-title-view__title-link::attr(href)").get()
        if court_page is None:
            court_name = response.css("div.search-business-snippet-view__title::text").get()
            if court_name is not None:
                # повторный запрос с названием из предложенного списка поиска
                time.sleep(2.5)
                yield scrapy.FormRequest.from_response(
                    response,
                    formdata={"text": court_name},
                    callback=self.follow_court_page,
                    meta={"proxy": "http://1c8cc108f81a3ae2349ddcf47ae22d1ba5563f2a:@proxy.zenrows.com:8001"}
                )
        else:
            is_court = response.css("a.business-categories-view__category::text").get()
            # некоторые суды в яндексе могут находиться в категории "администрация"
            if is_court == "Суд": 
                time.sleep(0.2)
                yield response.follow(
                    court_page, 
                    self.parse_court_info, 
                    meta={"proxy": "http://1c8cc108f81a3ae2349ddcf47ae22d1ba5563f2a:@proxy.zenrows.com:8001"}
                    )
        
    
    def parse_court_info(self, response):
        name = response.css("h1.orgpage-header-view__header::text").get()
        address = response.css("a.business-contacts-view__address-link::text").get()
        phone = response.css("div.orgpage-phones-view__phone-number::text").get()
        site = response.css("span.business-urls-view__text::text").get() 
        working_hours = response.xpath("//meta[@itemprop='openingHours']/@content").getall()
        count_of_reviews = response.css("div.tabs-select-view__title._name_reviews div.tabs-select-view__counter::text").get() 

        if response.css("div.tabs-select-view__title._name_reviews div.tabs-select-view__counter::text").get() is None:
            count_of_reviews = 0

        # достаём тип суда из названия
        splited_type = name.split(" ")
        if len(splited_type)<3:
            court_type = None
        else:
            court_type = f"{splited_type[1]} {splited_type[2]}"

        features = response.css("div.business-features-view__bool-list div.business-features-view__bool-text::text").getall()
        yield {
            "name": name,
            "address": address,
            "phone": phone,
            "working_hours": working_hours,
            "site": site,
            "count_of_reviews": count_of_reviews,
            "court_type": court_type,
            "features": features
            # "reviews": reviews
        }

        if count_of_reviews != 0:
            reviews_page = response.css("a.tabs-select-view__label::attr(href)")[2].get()
            yield response.follow(
                    reviews_page, 
                    self.parse_reviews_info, 
                    meta={"proxy": "http://1c8cc108f81a3ae2349ddcf47ae22d1ba5563f2a:@proxy.zenrows.com:8001"}
                )


    
    def parse_reviews_info(self, response):
        # reviews = []
        for review in response.css("div.business-review-view__info"):

            text = review.css("span.business-review-view__body-text::text").get()
            date = review.css("span.business-review-view__date meta::attr(content)").get() 
            username = review.css("a.business-review-view__link span::text").get()
            status = review.css("div.business-review-view__author-caption::text").get() 

            #stars = len(review.css("span.inline-image._loaded.icon.business-rating-badge-view__star._full"))
            
            reactions = [review.css("div.business-reactions-view__container")[0], review.css("div.business-reactions-view__container")[1]]
            likes = reactions[0].css("div.business-reactions-view__counter::text").get()
            dislikes = reactions[1].css("div.business-reactions-view__counter::text").get()

            if likes is None:
                likes = 0
            if dislikes is None:
                dislikes = 0

            yield {
                "text": text,
                "date": date,
                "username": username,
                "status": status,
                #"stars": stars,
                "likes": likes,
                "dislikes": dislikes
            }
