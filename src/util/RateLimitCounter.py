from time import sleep

class RateLimitCounter:
    def __init__(self, rate_sleep_time, rate_counter_limit) -> None:
        self.rate_sleep_time = rate_sleep_time
        self.rate_counter_limit = rate_counter_limit
        self.counter = 0
    def count(self):
        self.counter += 1
        if self.counter >= self.rate_counter_limit:
            self.counter = 0
            print("Sleeping for ", self.rate_sleep_time, "s")
            sleep(self.rate_sleep_time)