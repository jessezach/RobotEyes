import os
from optparse import OptionParser

from .report_generator import generate_report


def parse_options():
    parser = OptionParser()

    parser.add_option(
        '--baseline',
        dest='baseline',
        default=None,
        help="relative path to where baseline images directory exists"
    )

    parser.add_option(
        '--results',
        dest='results',
        default=os.getcwd(),
        help="relative path to where results directory exists"
    )

    opts, args = parser.parse_args()
    return parser, opts, args


def report_gen():
    root_folder = os.getcwd()
    parser, opts, arguments = parse_options()
    report_path = os.path.join(opts.results, 'output.xml')
    img_path = os.path.join(opts.results, 'visual_images')

    if opts.baseline is None:
        raise Exception('Please provide path to baseline image directory.')

    if os.path.exists(root_folder + "/" + report_path) and os.path.exists(root_folder + "/" + img_path):
        generate_report(opts.baseline, report_path, img_path)
    else:
        raise Exception("Please provide a valid path to results.")
