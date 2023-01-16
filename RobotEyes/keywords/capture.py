import os
import time

from ..utils import Utils


class CaptureKeywords(object):
    # Captures full screen
    def capture_full_screen(
        self,
        tolerance=None,
        blur=[],
        radius=50,
        name=None,
        redact=[]
    ):
        tolerance = self._get_tolerance(tolerance)
        name = self._get_image_name(name)
        path = os.path.join(self.path, name)
        self.browser.capture_full_screen(path, blur, radius, redact)
        self._post_capture_actions(path, name, tolerance)

    # Captures a specific region in a mobile screen
    def capture_mobile_element(
        self,
        selector,
        tolerance=None,
        blur=[],
        radius=50,
        name=None,
        redact=[]
    ):
        tolerance = self._get_tolerance(tolerance)
        name = self._get_image_name(name)
        path = os.path.join(self.path, name)
        self.browser.capture_mobile_element(selector, path, blur, radius, redact)
        self._post_capture_actions(path, name, tolerance)

    # Captures a specific region in a webpage
    def capture_element(
        self,
        selector,
        tolerance=None,
        blur=[],
        radius=50,
        name=None,
        redact=[]
    ):
        tolerance = self._get_tolerance(tolerance)
        name = self._get_image_name(name)
        path = os.path.join(self.path, name)
        time.sleep(1)
        self.browser.capture_element(path, selector, blur, radius, redact)
        self._post_capture_actions(path, name, tolerance)

    def scroll_to_element(self, selector):
        self.browser.scroll_to_element(selector)

    def _get_image_name(self, name):
        name = name or self._get_name()
        name += '.png'
        return name

    def _post_capture_actions(self, path, name, tolerance):
        test_name = self.test_name.replace(' ', '_')
        base_image = os.path.join(self.baseline_dir, test_name, name)
        Utils.fix_base_img_size_if_needed(base_image, path)
        self.stats[name] = tolerance
        self.count += 1
