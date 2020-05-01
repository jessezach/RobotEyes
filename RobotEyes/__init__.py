from datetime import datetime
import shutil
import time
from threading import Thread

from PIL import Image
from robot.libraries.BuiltIn import BuiltIn

from .constants import *
from .report_utils import *
from .imagemagick import Imagemagick
from .selenium_hooks import SeleniumHooks
from .report_generator import generate_report


class RobotEyes(object):
    output_dir = ''
    images_base_folder = ''
    test_name = ''
    baseline_dir = ''
    browser = None
    ROBOT_LISTENER_API_VERSION = 2
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    # Keeping this arg to avoid exceptions for those who have added tolerance in the previous versions.
    def __init__(self, tolerance=0):
        self.ROBOT_LIBRARY_LISTENER = self

    def open_eyes(self, lib='SeleniumLibrary', tolerance=0):
        self.tolerance = float(tolerance)
        self.tolerance = self.tolerance / 100 if self.tolerance >= 1 else self.tolerance
        self.stats = {}
        self.fail = False
        self.baseline_dir = self._get_baseline_dir()
        self.output_dir = self._output_dir()
        self.images_base_folder = os.path.join(self.output_dir, IMAGES_FOLDER)
        self.browser = SeleniumHooks(lib)
        self.test_name = BuiltIn().replace_variables('${TEST NAME}')
        test_name_folder = self.test_name.replace(' ', '_')
        # delete if directory already exist. Fresh test
        self._delete_folder_if_exists(test_name_folder)
        # recreate deleted folder
        self._create_empty_folder(test_name_folder)

    # Captures full screen
    def capture_full_screen(self, tolerance=None, blur=[], radius=50):
        tolerance = float(tolerance) if tolerance else self.tolerance
        tolerance = tolerance/100 if tolerance >= 1 else tolerance
        count = self.browser.capture_full_screen(self.path, blur, radius)
        if self.browser.is_mobile():
            self._fix_base_image_size(self.path + '/img' + str(count) + '.png', count)
        else:
            self._resize(self.path + '/img' + str(count) + '.png')
        key = 'img' + str(count) + '.png'
        self.stats[key] = tolerance

    # Captures a specific region in a mobile screen
    def capture_mobile_element(self, selector, tolerance=None, blur=[], radius=50):
        tolerance = float(tolerance) if tolerance else self.tolerance
        count = self.browser.capture_mobile_element(selector, self.path, blur, radius)
        key = 'img' + str(count) + '.png'
        self.stats[key] = tolerance

    # Captures a specific region in a webpage
    def capture_element(self, selector, tolerance=None, blur=[], radius=50):
        tolerance = float(tolerance) if tolerance else self.tolerance
        tolerance = tolerance/100 if tolerance >= 1 else tolerance
        time.sleep(1)
        count = self.browser.capture_element(self.path, selector, blur, radius)
        key = 'img' + str(count) + '.png'
        self.stats[key] = tolerance

    def scroll_to_element(self, selector):
        self.browser.scroll_to_element(selector)

    def compare_images(self):
        test_name = self.test_name.replace(' ', '_')
        baseline_path = os.path.join(self.baseline_dir, test_name)
        actual_path = os.path.join(self.images_base_folder, ACTUAL_IMAGE_BASE_FOLDER, test_name)
        diff_path = os.path.join(self.images_base_folder, DIFF_IMAGE_BASE_FOLDER, test_name)

        if not os.path.exists(diff_path):
            os.makedirs(diff_path)

        # compare actual and baseline images and save the diff image
        for filename in os.listdir(actual_path):
            if filename.endswith('.png'):
                b_path = os.path.join(baseline_path, filename)
                a_path = os.path.join(actual_path, filename)
                d_path = os.path.join(diff_path, filename)

                if os.path.exists(b_path):
                    difference = Imagemagick(b_path, a_path, d_path).compare_images()

                    try:
                        threshold = float(self.stats[filename])
                    except ValueError:
                        raise Exception('Invalid tolerance: %s' % self.stats[filename])

                    color, result = self._get_result(difference, threshold)
                    text = '%s %s' % (result, color)
                else:
                    shutil.copy(a_path, b_path)
                    text = '%s %s' % ('None', 'green')

                output = open(actual_path + '/' + filename + '.txt', 'w')
                output.write(text)
                output.close()
        BuiltIn().run_keyword('Fail', 'Image dissimilarity exceeds tolerance') if self.fail else ''

    def _delete_folder_if_exists(self, test_name_folder):
        actual_image_test_folder = os.path.join(self.images_base_folder, ACTUAL_IMAGE_BASE_FOLDER, test_name_folder)
        diff_image_test_folder = os.path.join(self.images_base_folder, DIFF_IMAGE_BASE_FOLDER, test_name_folder)

        if os.path.exists(actual_image_test_folder):
            shutil.rmtree(actual_image_test_folder)

        if os.path.exists(diff_image_test_folder):
            shutil.rmtree(diff_image_test_folder)

    def _create_empty_folder(self, test_name_folder):
        self.path = os.path.join(self.baseline_dir, test_name_folder)

        if not os.path.exists(self.path):
            os.makedirs(self.path)

        self.path = os.path.join(self.images_base_folder, ACTUAL_IMAGE_BASE_FOLDER, test_name_folder)

        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def _resize(self, *args):
        for arg in args:
            img = Image.open(arg)
            img = img.resize((1024, 700), Image.ANTIALIAS)
            img.save(arg)

    def _fix_base_image_size(self, path, count):
        test_name = self.test_name.replace(' ', '_')
        image_name = 'img' + str(count) + '.png'
        base_image = os.path.join(self.baseline_dir, test_name, image_name)
        if os.path.exists(base_image):
            im = Image.open(path)
            width, height = im.size
            im.close()

            im = Image.open(base_image)
            b_width, b_height = im.size
            if width != b_width or height != b_height:
                im = im.resize((width, height), Image.ANTIALIAS)
                im.save(base_image)

    def _delete_report_if_old(self, path):
        t1 = datetime.fromtimestamp(os.path.getmtime(path))
        t2 = datetime.now()
        diff = (t2 - t1).seconds
        os.remove(path) if diff > REPORT_EXPIRATION_THRESHOLD else ''

    def _output_dir(self):
        output_dir = BuiltIn().replace_variables('${OUTPUT DIR}')

        if 'pabot_results' in output_dir:
            index = output_dir.find('/pabot_results')
            return output_dir[:index]
        return output_dir

    def _get_result(self, difference, threshold):
        difference, threshold = int(difference*100), int(threshold*100)
        if difference > threshold:
            color = 'red'
            result = '%s<%s' % (threshold, difference)
            self.fail = True
        elif difference == threshold:
            color = 'green'
            result = '%s==%s' % (threshold, difference)
        else:
            color = 'green'
            result = '%s>%s' % (threshold, difference)
        return color, result

    def _get_baseline_dir(self):
        try:
            baseline_dir = BuiltIn().get_variable_value('${images_dir}')
        except:
            raise Exception('Please provide image baseline directory. Ex: -v images_dir:base')

        baseline_dir = os.path.join(os.getcwd(), baseline_dir)
        os.makedirs(baseline_dir) if not os.path.exists(baseline_dir) else ''
        return baseline_dir

    def _close(self):
        thread = Thread(
            target=generate_report,
            args=(self.baseline_dir, os.path.join(self.output_dir, 'output.xml'), self.images_base_folder, )
        )
        thread.start()
