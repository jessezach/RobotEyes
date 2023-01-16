from threading import Thread

from .keywords import CaptureKeywords, CompareKeywords, SetupKeywords
from .constants import *
from .report_utils import *


class RobotEyes(CaptureKeywords, CompareKeywords, SetupKeywords):
    ROBOT_LISTENER_API_VERSION = ROBOT_LISTENER_API_VERSION
    ROBOT_LIBRARY_SCOPE = ROBOT_LIBRARY_SCOPE

    # Keeping this arg to avoid exceptions for those who have added tolerance in the previous versions.
    def __init__(self, tolerance=0):
        self.ROBOT_LIBRARY_LISTENER = self
        self.lib = 'none'

    def _end_test(self, data, test):
        if hasattr(self, 'lib') and self.lib.lower() == 'none':
            if self.fail:
                test.status = 'FAIL'
                test.message = 'Image dissimilarity exceeds tolerance'

    def _close(self):
        if self.baseline_dir and self.output_dir:
            thread = Thread(
                target=ReportUtils.generate_report,
                args=(self.baseline_dir, self.output_dir, self.actual_dir,)
            )
            thread.start()
