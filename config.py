import pyotp
import argparse
import os
import json
import urllib.parse
import logging


def getEmptyConfig():
    return {
        "config": None,
        "headless": None,
        "email": None,
        "password": None,
        "code": None,
        "secret": None,
        "logging": None,
        "user_data": None,
        "wait_time": None,
        "max_hours": None,
        "max_failed": None,
        "timeout": None,
        "search_query": None,
        "blacklist": {
            "company": [],
            "title": []
        }
    }


class Config:
    def __init__(self):
        self.list = {}
        self.config = getEmptyConfig()
        cliconfig = self.parseArguments()
        envconfig = self.parseEnvironment()
        self.parseJSONConfig(file=cliconfig["config"])
        self.mergeConfig(envconfig)
        self.mergeConfig(cliconfig)

    def mergeConfig(self, config={}):
        for k in self.config.keys():
            if k in config and config[k] is not None:
                if k == "blacklist":
                    blacklist = self.config[k]
                    for bk in blacklist.keys():
                        if bk in config[k] and config[k][bk] is not None:
                            nlist = list(self.config[k][bk])
                            nlist.extend(
                                x for x in config[k][bk] if x not in self.config[k][bk])
                            self.config[k][bk] = nlist
                else:
                    self.config[k] = config[k]

    def parseJSONConfig(self, file="./config.json"):
        f = open(file)
        config = json.load(f)
        self.mergeConfig(config)

    def parseEnvironment(self):
        config = getEmptyConfig()
        if "CI" in os.environ:
            config["headless"] = True
        if "LEAB_BLACKLIST_TITLE" in os.environ and os.environ["LEAB_BLACKLIST_TITLE"] != "":
            config["blacklist"]["title"] = os.environ["LEAB_BLACKLIST_TITLE"].split(
                ",")
        if "LEAB_BLACKLIST_COMPANY" in os.environ and os.environ["LEAB_BLACKLIST_COMPANY"] != "":
            config["blacklist"]["company"] = os.environ["LEAB_BLACKLIST_COMPANY"].split(
                ",")
        if "LEAB_SEARCH_QUERY" in os.environ and os.environ["LEAB_SEARCH_QUERY"] != "":
            config["search_query"] = urllib.parse.parse_qs(
                os.environ["LEAB_SEARCH_QUERY"])
        for k in config.keys():
            if config[k] is None:
                envkey = "LEAB_"+str(k.upper())
                if envkey in os.environ and os.environ[envkey] != "":
                    config[k] = os.environ[envkey]
        return config

    def parseArguments(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--headless', action='store_true')
        parser.add_argument('--config', default='./config.json')
        parser.add_argument('--email')
        parser.add_argument('--password')
        parser.add_argument('--code')
        parser.add_argument('--secret')
        parser.add_argument('--logging')
        parser.add_argument('--user-data')
        parser.add_argument('--wait-time')
        parser.add_argument('--max-hours')
        parser.add_argument('--max-failed')
        parser.add_argument('--timeout')
        parser.add_argument('--search-query')
        parser.add_argument('--blacklist-company')
        parser.add_argument('--blacklist-title')
        args = parser.parse_args()
        config = getEmptyConfig()
        if args.headless:
            config["headless"] = True
        if args.blacklist_title is not None:
            config["blacklist"]["title"] = args.blacklist_title.split(",")
        if args.blacklist_company is not None:
            config["blacklist"]["company"] = args.blacklist_company.split(",")
        if args.search_query is not None:
            config["search_query"] = urllib.parse.parse_qs(args.search_query)
        argvars = vars(args)
        for k in config.keys():
            if config[k] is None:
                if argvars[k] is not None and k != "headless":
                    config[k] = argvars[k]
        return config

    def get(self, name, default=None):
        if name == "code" and self.config["code"] is None:
            secret = self.get("secret")
            if secret is not None:
                return pyotp.TOTP(secret).now()
        if self.config[name] is not None:
            return self.config[name]
        return default

    # TODO: add multible logger types
    # TODO: add multible logger levels for each type
    def getLogger(self, suffix=None):
        logger = logging.getLogger("main")
        logger.setLevel(self.get("logging", "WARN"))
        if logger.hasHandlers() is False:
            loghandler = logging.StreamHandler()
            loghandler.setFormatter(logging.Formatter("%(message)s"))
            logger.addHandler(loghandler)
        if suffix is not None:
            return logger.getChild(suffix)
        return logger

    # TODO: add multible reporter types
    def saveJob(self, jobId, status):
        self.list[jobId] = status

    def getJobsByStatus(self, status):
        list = []
        for j in self.list.keys():
            if self.list[j] in status:
                list.append(j)
        return list

    def getJob(self, jobId):
        if jobId in self.list:
            return self.list[jobId]
        return None

    def checkBlacklist(self, blType, value):
        blacklist = self.get("blacklist")
        if blacklist is not None:
            if blType in blacklist:
                if any([x in value for x in blacklist[blType]]):
                    return True
        return False

    def printReport(self):
        applied = self.getJobsByStatus(["applied"])
        already = self.getJobsByStatus(["already"])
        timeout = self.getJobsByStatus(["timeout"])
        manual = self.getJobsByStatus(["manual"])
        self.getLogger().warn("%d Applications Submitted, %d Already Applied, %d Timed Out, %d Manual Action Required",
                              len(applied), len(already), len(timeout), len(manual))
        for job in self.getJobsByStatus(["timeout","manual"]):
            self.getLogger().warn("https://www.linkedin.com/jobs/view/%s/" % job)

    def print(self):
        print(json.dumps(self.config))


if __name__ == "__main__":
    config = Config()
    config.print()
