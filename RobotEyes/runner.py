from . import web
import sys


def main():
    try:
        results = sys.argv[1]
    except IndexError:
        results = ''

    try:
        host = sys.argv[2]
    except IndexError:
        host = '127.0.0.1'

    try:
        port = sys.argv[3]
    except IndexError:
        port = 5000

    web.start(results, host, port)
