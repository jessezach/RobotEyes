from optparse import OptionParser

from . import web


def parse_options():
    parser = OptionParser()

    parser.add_option(
        '--results',
        dest='results',
        default='',
        help="relative path to results folder where visual_images directory exists"
    )

    parser.add_option(
        '--baseline',
        dest='baseline',
        default=None,
        help="relative path to results folder where visual_images directory exists"
    )

    parser.add_option(
        '--host',
        dest='host',
        default='0.0.0.0',
        help="host on which server should run"
    )

    parser.add_option(
        '--port',
        dest='port',
        default=5000,
        help="port on which server should run"
    )
    opts, args = parser.parse_args()
    return parser, opts, args


def main():
    parser, opts, arguments = parse_options()

    web.start(opts.baseline, opts.results, opts.host, opts.port)
