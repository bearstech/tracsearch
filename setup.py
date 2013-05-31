from distutils.core import setup


setup(name='tracsearch',
      version='0.5',
      author='Mathieu Lecarme',
      author_email='mlecarme@bearstech.com',
      license='BSD',
      packages=['tracsearch'],
      scripts=['scripts/tracsearch'],
      requires=['flask',
                'pyelasticsearch(==0.5)',
                'raven',
                'blinker',
                'requests',
                'docopt'
                ]
      )
