import os
import shutil
import time
import subprocess
import platform
import math

from PIL import Image, ImageFilter
from robot.libraries.BuiltIn import BuiltIn

from .constants import *


class RobotEyes(object):
    output_dir = ''
    images_base_folder = ''
    driver = None
    test_name = ''
    count = 0

    def __init__(self, mode, tolerance=0):
        self.mode = mode
        self.sys = platform.system()
        self.tolerance = tolerance

    def open_eyes(self, lib='Selenium2Library'):
        self.output_dir = BuiltIn().replace_variables('${OUTPUT DIR}')
        self.images_base_folder = self.output_dir + IMAGES_FOLDER

        try:
            s2l = BuiltIn().get_library_instance(lib)

            if lib == 'AppiumLibrary':
                self.driver = s2l._current_application()
            else:
                self.driver = s2l._current_browser()

        except RuntimeError:
            raise Exception('%s instance not found' % lib)

        self.test_name = BuiltIn().replace_variables('${TEST NAME}')
        self.count = 1
        test_name_folder = self.test_name.replace(' ', '_')

        # delete if directory already exist. Fresh test
        self._delete_folder_if_exists(test_name_folder)

        # recreate deleted folder
        self._create_empty_folder(test_name_folder)

    # Captures full screen
    def capture_full_screen(self, tolerance=None, blur=[], radius=50):
        if not tolerance:
            tolerance = self.tolerance
        self.driver.save_screenshot(self.path + '/img' + str(self.count) + '.png')

        if blur:
            self._blur_regions(blur, radius)

        if self.mode.lower() == MODE_TEST:
            output = open(self.path + '/img' + str(self.count) + '.png.txt', 'w')
            output.write(str(tolerance))
            output.close()
        self.count += 1

    # Captures a specific region in a mobile screen
    def capture_mobile_element(self, selector, tolerance=None):
        if not tolerance:
            tolerance = self.tolerance

        prefix, locator, search_element = self._find_element(selector)

        location = search_element.location
        size = search_element.size
        self.driver.save_screenshot(self.path + '/img' + str(self.count) + '.png')

        left = location['x']
        top = location['y']
        right = location['x'] + size['width']
        bottom = location['y'] + size['height']
        image = Image.open(self.path + '/img' + str(self.count) + '.png')
        image = image.crop((left, top, right, bottom))
        image.save(self.path + '/img' + str(self.count) + '.png')

        if self.mode.lower() == MODE_TEST:
            output = open(self.path + '/img' + str(self.count) + '.png.txt', 'w')
            output.write(str(tolerance))
            output.close()
        self.count += 1

    # Captures a specific region in a webpage
    def capture_element(self, selector, tolerance=None, blur=[], radius=50):
        if not tolerance:
            tolerance = self.tolerance

        prefix, locator, _ = self._find_element(selector)
        time.sleep(1)
        self.driver.save_screenshot(self.path + '/img' + str(self.count) + '.png')

        coord = self._get_coordinates(prefix, locator)
        left = math.ceil(coord['left'])
        top = math.ceil(coord['top'])
        right = math.ceil(coord['right'])
        bottom = math.ceil(coord['bottom'])

        if blur:
            self._blur_regions(blur, radius)

        im = Image.open(self.path + '/img' + str(self.count) + '.png')

        if self.sys.lower() == "darwin":
            im = im.crop((left + left, top + top, right + right, bottom + bottom))
        else:
            im = im.crop((left, top, right, bottom))

        im.save(self.path + '/img' + str(self.count) + '.png')

        if self.mode.lower() == MODE_TEST:
            output = open(self.path + '/img' + str(self.count) + '.png.txt', 'w')
            output.write(str(tolerance))
            output.close()
        self.count += 1

    def scroll_to_element(self, selector):
        prefix, locator, search_element = self._find_element(selector)
        self.driver.execute_script("return arguments[0].scrollIntoView();", search_element)

    def compare_images(self):
        if self.mode.lower() == MODE_TEST:
            test_name = self.test_name.replace(' ', '_')
            baseline_path = self.images_base_folder + BASELINE_IMAGE_BASE_FOLDER + test_name
            actual_path = self.images_base_folder + ACTUAL_IMAGE_BASE_FOLDER + test_name
            diff_path = self.images_base_folder + DIFF_IMAGE_BASE_FOLDER + test_name

            if not os.path.exists(diff_path):
                os.makedirs(diff_path)

            # compare actual and baseline images and save the diff image
            for filename in os.listdir(actual_path):
                a_path = ''
                b_path = ''
                d_path = ''

                if filename.endswith('.png'):
                    b_path = baseline_path + '/' + filename
                    a_path = actual_path + '/' + filename
                    d_path = diff_path + '/' + filename

                    if os.path.exists(b_path):
                        difference = self._compare(b_path, a_path, d_path)
                        fname = open(actual_path + '/' + filename + '.txt', 'r')
                        threshold = float(fname.readline())
                        fname.close()

                        if difference > threshold:
                            color = 'red'
                            result = '%s<%s' % (threshold, difference)

                        elif difference == threshold:
                            color = 'green'
                            result = '%s==%s' % (threshold, difference)

                        else:
                            color = 'green'
                            result = '%s>%s' % (threshold, difference)

                        text = '%s %s' % (result, color)

                        output = open(actual_path + '/' + filename + '.txt', 'w')
                        output.write(text)
                        output.close()
                    else:
                        raise Exception('Baseline image does not exist for %s in test %s' % (filename, test_name))

    def _compare(self, b_path, a_path, d_path):
        im = Image.open(b_path)
        b_width, b_height = im.size
        im.close()

        im = Image.open(a_path)
        a_width, a_height = im.size
        im.close()

        b_area = int(b_width) * int(b_height)
        a_area = int(a_width) * int(a_height)
        
        large_image = a_path
        small_image = b_path
        
        if b_area > a_area:
            large_image = b_path
            small_image = a_path
            
        compare_cmd = 'compare -metric RMSE -subimage-search -dissimilarity-threshold 1.0 %s %s %s' \
                      % (large_image, small_image, d_path)

        proc = subprocess.Popen(compare_cmd,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out, err = proc.communicate()
        print(err)
        return float(err.split()[1][1:-1])

    def _find_element(self, selector):
        if selector.startswith('//'):
            prefix = 'xpath'
            locator = selector
        else:
            selector_parts = selector.partition('=')
            prefix = selector_parts[0].strip()
            locator = selector_parts[2].strip()
            if not locator:
                raise Exception('Please prefix locator type.')
        dict = {
            'xpath': self.driver.find_element_by_xpath,
            'id': self.driver.find_element_by_id,
            'class': self.driver.find_element_by_class_name,
            'css': self.driver.find_element_by_css_selector
        }
        if prefix.lower() not in dict:
            raise Exception('Please add a valid locator prefix. Eg xpath, css, class.')
            
        func = dict[prefix.lower()]
        search_element = func(locator)
        return prefix, locator, search_element

    def _get_coordinates(self, prefix, locator):
        if prefix.lower() == 'xpath':
            locator = locator.replace('"', "'")
            cmd = "var e = document.evaluate(\"{0}\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null)" \
                  ".singleNodeValue;return e.getBoundingClientRect();".format(locator)
            coord = self.driver.execute_script(cmd)
        elif prefix.lower() == 'css':
            locator = locator.replace('"', "'")
            cmd = "var e = document.querySelector(\"{0}\");return e.getBoundingClientRect();".format(locator)
            coord = self.driver.execute_script(cmd)
        elif prefix.lower() == 'id':
            cmd = "var e = document.getElementById(\"{0}\");return e.getBoundingClientRect();".format(locator)
            coord = self.driver.execute_script(cmd)
        elif prefix.lower() == 'class':
            cmd = "var e = document.getElementsByClassName(\"{0}\")[0];return e.getBoundingClientRect();" \
                .format(locator)
            coord = self.driver.execute_script(cmd)
        return coord

    def _delete_folder_if_exists(self, test_name_folder):
        if self.mode.lower() == MODE_TEST:
            if os.path.exists(self.images_base_folder + ACTUAL_IMAGE_BASE_FOLDER + test_name_folder):
                shutil.rmtree(self.images_base_folder + ACTUAL_IMAGE_BASE_FOLDER + test_name_folder)

            if os.path.exists(self.images_base_folder + DIFF_IMAGE_BASE_FOLDER + test_name_folder):
                shutil.rmtree(self.images_base_folder + DIFF_IMAGE_BASE_FOLDER + test_name_folder)

        elif self.mode.lower() == MODE_BASELINE:
            if os.path.exists(self.images_base_folder + BASELINE_IMAGE_BASE_FOLDER + test_name_folder):
                shutil.rmtree(self.images_base_folder + BASELINE_IMAGE_BASE_FOLDER + test_name_folder)

        else:
            raise AssertionError('Mode should be test or baseline')

    def _create_empty_folder(self, test_name_folder):
        if self.mode.lower() == MODE_BASELINE:
            self.path = self.images_base_folder + BASELINE_IMAGE_BASE_FOLDER + test_name_folder

        elif self.mode.lower() == MODE_TEST:
            self.path = self.images_base_folder + ACTUAL_IMAGE_BASE_FOLDER + test_name_folder

        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def _blur_regions(self, selectors, radius):
        if not isinstance(selectors, list):
            selectors = [selectors]

        for region in selectors:
            prefix, locator, _ = self._find_element(region)
            area_coordinates = self._get_coordinates(prefix, locator)

            left = math.ceil(area_coordinates['left'])
            top = math.ceil(area_coordinates['top'])
            right = math.ceil(area_coordinates['right'])
            bottom = math.ceil(area_coordinates['bottom'])

            im = Image.open(self.path + '/img' + str(self.count) + '.png')

            if self.sys.lower() == "darwin":
                cropped_image = im.crop((left + left, top + top, right + right, bottom + bottom))
            else:
                cropped_image = im.crop((left, top, right, bottom))

            blurred_image = cropped_image.filter(ImageFilter.GaussianBlur(radius=radius))

            if self.sys.lower() == "darwin":
                im.paste(blurred_image, (left + left, top + top, right + right, bottom + bottom))
            else:
                im.paste(blurred_image, (left, top, right, bottom))

            im.save(self.path + '/img' + str(self.count) + '.png')