from ConfigParser import SafeConfigParser


class Config(SafeConfigParser):

    def _loop(self, pattern):
        for section in self.sections():
            s = section.split(':')
            if len(s) > 1 and s[0] == pattern:
                yield section

    def tracs(self):
        for t in self._loop('trac'):
            yield t

    def redmines(self):
        for r in self._loop('redmine'):
            yield r


config = Config()
config.read(['tracsearch.ini'])
