from PIL import Image
import subprocess
import os, shutil, time
from robot.libraries.BuiltIn import BuiltIn
import platform


class RobotEyes(object):
    def __init__(self, mode, tolerance=0):
        self.mode = mode
        self.sys = platform.system()
        self.tolerance = tolerance

    def open_eyes(self):
        self.output_dir = BuiltIn().replace_variables('${OUTPUT DIR}')
        self.report_folder = self.output_dir + '/visual_images'

        try:
            s2l = BuiltIn().get_library_instance('Selenium2Library')
            self.driver = s2l._current_browser()
        except:
            try:
                appiumlib = BuiltIn().get_library_instance('AppiumLibrary')
                self.driver = appiumlib._current_application()
            except:
                raise ValueError('Browser/App is not open')

        self.test_name = BuiltIn().replace_variables('${TEST NAME}')
        self.count = 1
        test_name = self.test_name.replace(' ', '_')

        if self.mode.lower() == 'test':
            if os.path.exists(self.report_folder + '/actual/' + test_name):
                shutil.rmtree(self.report_folder + '/actual/' + test_name)

            if os.path.exists(self.report_folder + '/diff/' + test_name):
                shutil.rmtree(self.report_folder + '/diff/' + test_name)
        elif self.mode.lower() == 'baseline':
            if os.path.exists(self.report_folder + '/baseline/' + test_name):
                shutil.rmtree(self.report_folder + '/baseline/' + test_name)
        else:
            raise ValueError('Mode should be test or baseline')

        if self.mode.lower() == 'baseline':
            self.path = self.report_folder + '/baseline/' + test_name
        elif self.mode.lower() == 'test':
            self.path = self.report_folder + '/actual/' + test_name

        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def capture_full_screen(self, tolerance=None):
        print 'Capturing page...'
        if not tolerance:
            tolerance = self.tolerance
        self.driver.save_screenshot(self.path + '/img' + str(self.count) + '.png')
        if self.mode.lower() == 'test':
            output = open(self.path + '/img' + str(self.count) + '.png.txt', 'w')
            output.write(str(tolerance))
            output.close()
        self.count += 1

    def capture_mobile_element(self, selector):

        prefix, locator, search_element = self.element_finder(selector)

        location = search_element.location
        size = search_element.size
        self.driver.save_screenshot(self.path + '/img' + str(self.count) + '.png')

        left = location['x']
        top = location['y']
        right = location['x'] + size['width']
        bottom = location['y'] + size['height']
        im = Image.open(self.path + '/img' + str(self.count) + '.png')
        im = im.crop((left, top, right, bottom))  # defines crop points
        im.save(self.path + '/img' + str(self.count) + '.png')
        self.count += 1

    def capture_element(self, selector, tolerance=None):

        if not tolerance:
            tolerance = self.tolerance

        prefix, locator, search_element = self.element_finder(selector)
        time.sleep(1)
        self.driver.save_screenshot(self.path + '/img' + str(self.count) + '.png')
        coord = self.get_js_coords(prefix, locator)
        left = coord['left']
        top = coord['top']
        right = coord['right']
        bottom = coord['bottom']

        im = Image.open(self.path + '/img' + str(self.count) + '.png')
        if self.sys.lower() == "darwin":
            im = im.crop((left + left, top + top, right + right, bottom + bottom))  # defines crop points
        else:
            im = im.crop((left, top, right, bottom))  # defines crop points
        im.save(self.path + '/img' + str(self.count) + '.png')

        if self.mode.lower() == 'test':
            output = open(self.path + '/img' + str(self.count) + '.png.txt', 'w')
            output.write(str(tolerance))
            output.close()
        self.count += 1

    def scroll_to_element(self, selector):
        prefix, locator, search_element = self.element_finder(selector)
        self.driver.execute_script("return arguments[0].scrollIntoView();", search_element)

    def compare_images(self):
        if self.mode.lower() == 'test':
            test_name = self.test_name.replace(' ', '_')
            baseline_path = self.report_folder + '/baseline/' + test_name
            actual_path = self.report_folder + '/actual/' + test_name
            diff_path = self.report_folder + '/diff/' + test_name

            # compare actual and baseline images and save the diff image
            for filename in os.listdir(actual_path):
                if filename.endswith('.png'):
                    a_path = ''
                    b_path = ''
                    d_path = ''

                    if not os.path.exists(diff_path):
                        os.makedirs(diff_path)

                    b_path = baseline_path + '/' + filename
                    a_path = actual_path + '/' + filename
                    d_path = diff_path + '/' + filename

                    if os.path.exists(b_path):
                        im = Image.open(b_path)
                        b_width, b_height = im.size
                        im.close()
                        im = Image.open(a_path)
                        a_width, a_height = im.size
                        im.close()

                        b_area = int(b_width) * int(b_height)
                        a_area = int(a_width) * int(a_height)

                        if b_area > a_area:
                            large_image = b_path
                            small_image = a_path
                        else:
                            large_image = a_path
                            small_image = b_path

                        compare_cmd = 'compare -metric RMSE -subimage-search -dissimilarity-threshold 1.0 %s %s %s' \
                                      % (large_image, small_image, d_path)

                        proc = subprocess.Popen(compare_cmd,
                                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                        out, err = proc.communicate()
                        print err
                        difference = float(err.split()[1][1:-1])

                        fname = open(actual_path + '/' + filename + '.txt', 'r')
                        threshold = float(fname.readline())
                        fname.close()

                        if difference > threshold:
                            color = 'red'
                            result = '%s<%s' % (threshold, difference)
                        else:
                            color = 'green'
                            result = '%s>=%s' % (threshold, difference)

                        text = '%s %s' % (result, color)

                        output = open(actual_path + '/' + filename + '.txt', 'w')
                        output.write(text)
                        output.close()
                    else:
                        print 'Baseline image does not exist..'

    def element_finder(self, selector):
        if selector.startswith('//'):
            prefix = 'xpath'
            locator = selector
        else:
            selector_parts = selector.partition('=')
            prefix = selector_parts[0].strip()
            locator = selector_parts[2].strip()
            if not locator:
                raise ValueError('Please prefix locator type.')

        if prefix.lower() == 'xpath':
            search_element = self.driver.find_element_by_xpath(locator)
        elif prefix.lower() == 'id':
            search_element = self.driver.find_element_by_id(locator)
        elif prefix.lower() == 'class':
            search_element = self.driver.find_element_by_class_name(locator)
        elif prefix.lower() == 'css':
            search_element = self.driver.find_element_by_css_selector(locator)
        return prefix, locator, search_element

    def get_js_coords(self, prefix, locator):
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
