import datetime
from scrapy import signals
from scrapy.exceptions import CloseSpider
from scrapy.signalmanager import dispatcher

class TimeLimitMiddleware:
    def __init__(self, crawler, time_limit):
        self.start_time = datetime.datetime.now()
        self.time_limit = datetime.timedelta(minutes=time_limit)
        dispatcher.connect(self.spider_closed, signal=signals.spider_closed)
        dispatcher.connect(self.scheduler_closed, signal=signals.scheduler_closed)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler, time_limit=crawler.settings.getfloat('SCRAPY_TIME_LIMIT', 30))

    def scheduler_closed(self, reason):
        elapsed_time = datetime.datetime.now() - self.start_time
        if elapsed_time > self.time_limit:
            raise CloseSpider(f"Time limit ({self.time_limit.total_seconds()} seconds) exceeded")

    def spider_closed(self, spider, reason):
        # Additional cleanup or actions can be performed here
        pass
