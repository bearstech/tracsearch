from urlparse import urlparse

import requests


class Redmine(object):

    def __init__(self, url):
        p = urlparse(url)
        self.url = "%s://%s" % (p.scheme, p.hostname)
        self.key = p.username
        self.headers = {
            'Content-Type': 'application/json',
            'X-Redmine-API-Key': self.key
        }

    def issues(self):
        r = requests.get("%s/issues.json" % self.url, headers=self.headers)
        assert r.status_code == 200
        return r.json()

if __name__ == '__main__':
    from config import config
    for r in config.redmines():
        redmine = Redmine(config.get(r, 'url'))
        print redmine.issues()
