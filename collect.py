import time
from collections import defaultdict


class TokenCounter:
    def __init__(self, interval=900):
        self.interval = interval
        self.pv = defaultdict(int)
        self.calls = defaultdict(int)
        self.tokens = defaultdict(int)

    def page_view(self):
        current_time = time.time()
        interval_time = int(current_time / self.interval)
        self.pv[interval_time] += 1
        self.calls[interval_time] += 0
        self.tokens[interval_time] += 0

    def collect(self, tokens=1):
        current_time = time.time()
        interval_time = int(current_time / self.interval)
        self.pv[interval_time] += 0
        self.calls[interval_time] += 1
        self.tokens[interval_time] += tokens

    def summary(self):
        pv_stats = {}
        call_stats = {}
        token_stats = {}
        for interval_time, calls in sorted(self.calls.items()):
            start_time = interval_time * self.interval
            end_time = (interval_time + 1) * self.interval - 1
            call_stats[time.ctime(start_time)] = calls
            token_stats[time.ctime(start_time)] = self.tokens[interval_time]
            pv_stats[time.ctime(start_time)] = self.pv[interval_time]
        return pv_stats, call_stats, token_stats
