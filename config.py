from ConfigParser import SafeConfigParser


class Config(SafeConfigParser):

    def tracs(self):
        for section in self.sections():
            s = section.split(':')
            if len(s) > 1 and s[0] == "trac":
                yield section


config = Config()
config.read(['tracsearch.ini'])
