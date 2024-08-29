import scrapy
import time
import json


class GetCourtsInfoSpider(scrapy.Spider):
    name = "get_courts_info"
    allowed_domains = ["yandex.ru"]
    start_urls = ["https://yandex.ru/maps/"]

    def __init__(self):
        self.proxy = "YOUR PROXY"

    def start_requests(self):

        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={"proxy": self.proxy}
            )

    def parse(self, response, **kwargs):
        # считываем названия судов
        courts_names = None
        path = "./data/courts_names_emails.json"
        try:
            with open(path, 'r', encoding='utf-8') as f:
                courts_names = json.load(f)
        except FileNotFoundError:
            print("cant open file")

        if courts_names is not None:
            # проходимся по каждому суду
            # for court in [courts_names[0]]:
            for court in courts_names:
                name = court['name']
                time.sleep(2)

                # ищем суд через поиск
                yield scrapy.FormRequest.from_response(
                    response,
                    formdata={"text": name},
                    callback=self.follow_court_page,
                    meta={
                        "proxy": self.proxy,
                        "name": name}
                )

    def follow_court_page(self, response):
        court_page = response.css("a.card-title-view__title-link::attr(href)").get()
        if court_page is None:
            court_name = response.css("div.search-business-snippet-view__title::text").get()
            if court_name is not None:
                # повторный запрос с названием из предложенного списка поиска
                time.sleep(1.5)
                yield scrapy.FormRequest.from_response(
                    response,
                    formdata={"text": court_name},
                    callback=self.follow_court_page,
                    meta={
                        "proxy": self.proxy,
                        "name": response.meta.get("name")
                        }
                )
        else:
            is_court = response.css("a.business-categories-view__category::text").get()
            # некоторые суды в яндексе могут находиться в категории "администрация", пропускаем их
            if is_court == "Суд":
                time.sleep(2)
                yield response.follow(
                    court_page,
                    self.parse_court_info,
                    meta={
                        "proxy": self.proxy,
                        "name": response.meta.get("name")
                        }
                )

    def parse_court_info(self, response):
        name = response.meta.get("name")
        name_yandex = response.css("h1.orgpage-header-view__header::text").get()
        address = response.css("a.business-contacts-view__address-link::text").get()
        phone = response.css("div.orgpage-phones-view__phone-number::text").get()
        site = response.css("span.business-urls-view__text::text").get()
        working_hours = response.xpath("//meta[@itemprop='openingHours']/@content").getall()
        count_of_reviews = response.css(
            "div.tabs-select-view__title._name_reviews div.tabs-select-view__counter::text").get()

        if response.css("div.tabs-select-view__title._name_reviews div.tabs-select-view__counter::text").get() is None:
            count_of_reviews = 0

        # достаём тип суда из названия
        splited_type = name.split(" ")
        if splited_type[1]== "суд":
             court_type = f"{splited_type[0].lower()} {splited_type[1]}"
        else:
            court_type = f"{splited_type[1]} {splited_type[2]}"

        features = response.css(
            "div.business-features-view__bool-list div.business-features-view__bool-text::text").getall()

        court_data = {
            "name": name,
            "name_yandex": name_yandex,
            "address": address,
            "phone": phone,
            "working_hours": working_hours,
            "site": site,
            "count_of_reviews": int(count_of_reviews),
            "court_type": court_type,
            "features": features
        }

        if count_of_reviews != 0:
            reviews_page = response.css("a.tabs-select-view__label::attr(href)")[2].get()
            yield response.follow(
                reviews_page,
                self.parse_reviews_info,
                meta={"proxy": self.proxy,
                      "court": court_data}
            )

    def parse_reviews_info(self, response):
        time.sleep(1.5)

        for review in response.css("div.business-review-view__info"):

            text = review.css("span.business-review-view__body-text::text").get()
            date = review.css("span.business-review-view__date meta::attr(content)").get()
            username = review.css("a.business-review-view__link span::text").get()
            status = review.css("div.business-review-view__author-caption::text").get()

            stars = len(review.css("div.business-rating-badge-view__stars "
                                   "span.inline-image.icon.business-rating-badge-view__star._full"))

            reactions = [review.css("div.business-reactions-view__container")[0],
                         review.css("div.business-reactions-view__container")[1]]
            likes = reactions[0].css("div.business-reactions-view__counter::text").get()
            dislikes = reactions[1].css("div.business-reactions-view__counter::text").get()

            if likes is None:
                likes = 0
            if dislikes is None:
                dislikes = 0

            court_data = response.meta.get('court')
            review = {
                "text": text,
                "date": date,
                "username": username,
                "status": status,
                "stars": stars,
                "likes": int(likes),
                "dislikes": int(dislikes)
            }

            court_data.update(review)
            yield court_data
