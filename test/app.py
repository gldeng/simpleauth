import os
import sys


dirname = os.path.abspath(os.path.dirname(__file__))

sys.path.insert(0, os.path.join(dirname, '..'))

from simpleauth import create_app

configfile = os.path.join(dirname, 'app.cfg')

app = create_app(configfile)


if __name__ == '__main__':
    app.run()
