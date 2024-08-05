import os
import pprint
import re
import gzip
import json
import logging
import statistics
from datetime import datetime
from statistics import median
from typing import LiteralString

import structlog

logger = structlog.get_logger()
log_pattern = re.compile(
    r'"(?:GET|POST|PUT|DELETE|HEAD) (?P<url>\S+) HTTP/\d\.\d".*?(?P<time>\d+\.\d+)$'
)


def create_abs_path(path) -> str:
    return str(os.path.join(os.path.dirname(os.path.abspath(__file__)), path))


class LinkInfo:
    def __init__(self):
        self.count = 0
        self.count_perc = 0
        self.time_sum = 0
        self.time_perc = 0
        self.time_avg = 0
        self.time_max = 0
        self.time_med = 0


class LogAnalyzer:
    def __init__(self, config_path):
        self.REPORT_SIZE = 1000
        self.REPORT_DIR = "reports"
        self.LOG_DIR = "logs"
        self.config_path = config_path
        self.latest_log = None
        self.dict_to_render = {}

        self.count_sum = None
        self.time_sum = None

        self.load_config()

    def load_config(self):
        directory_of_script = os.path.dirname(os.path.abspath(__file__))
        self.config_path = os.path.join(directory_of_script, self.config_path)
        if os.path.exists(self.config_path):
            with open(self.config_path, "r") as file:
                config = json.load(file)
                self.REPORT_SIZE = config["REPORT_SIZE"]
                self.REPORT_DIR = config["REPORT_DIR"]
                self.LOG_DIR = config["LOG_DIR"]
        else:
            logger.error("Config import error. Used default configuration.")
        self.find_latest_log()

    def find_latest_log(self):
        self.latest_log = sorted(os.listdir(create_abs_path(self.LOG_DIR)), reverse=True)[0]
        self.parse_log_file()

    def parse_log_file(self):
        for line in self.read_log_data():
            match = log_pattern.search(line)
            if match:
                url = match.group('url')
                time = float(match.group('time'))
                if url not in self.dict_to_render:
                    self.dict_to_render[url] = LinkInfo()
                    self.dict_to_render[url].count = 1
                    self.dict_to_render[url].time_sum = time
                    self.dict_to_render[url].time_max = time
                else:
                    self.dict_to_render[url].count += 1
                    self.dict_to_render[url].time_sum += time
                    self.dict_to_render[url].time_max = max(time, self.dict_to_render[url].time_max)

        self.analyze_log_data()

    def read_log_data(self):
        log_path = create_abs_path(f'{self.LOG_DIR}/{self.latest_log}')
        func_to_open = gzip.open if log_path.endswith('.gz') else open
        with func_to_open(log_path, 'rt') as log:
            for line in log:
                yield line

    def analyze_log_data(self):
        self.count_sum = 0
        self.time_sum = 0
        for value in self.dict_to_render.values():
            self.count_sum += value.count
            self.time_sum += value.time_sum

        for value in self.dict_to_render.values():
            value.count_perc = value.count / self.count_sum * 100
            value.time_perc = value.time_sum / self.time_sum * 100
            value.time_avg = value.time_sum / value.count

        self.render_report()

    def render_report(self):
        html_template = open(create_abs_path("templates/report.html"), "r").read()
        filled_html = html_template.format(table=self.generate_table())

        with open(create_abs_path("reports/report.html"), "w") as report_file:
            report_file.write(filled_html)

    def generate_table(self):
        rows = ""
        sorted_logs = sorted(self.dict_to_render.items(), key=lambda x: x[1].time_sum, reverse=True)
        for url, stats in sorted_logs[:self.REPORT_SIZE]:
            row = f"<tr>" \
                  f"<td>{url}</td>" \
                  f"<td>{stats.count}</td>" \
                  f"<td>{stats.count_perc}</td>" \
                  f"<td>{stats.time_sum}</td>" \
                  f"<td>{stats.time_perc}</td>" \
                  f"<td>{stats.time_avg}</td>" \
                  f"<td>{stats.time_max}</td>" \
                  f"<td>{stats.time_med}</td>" \
                  f"</tr>\n"
            rows += row
        return (f"<table><thead><tr><th>URL</th><th>count</th><th>count_perc</th><th>time_sum</th><th"
                f">time_perc</th><th>time_avg</th><th>time_max</th><th>time_med</th></tr></thead><tbody>{rows}</tbody"
                f"></table>")


def main():
    LogAnalyzer("config.json")


if __name__ == "__main__":
    main()
