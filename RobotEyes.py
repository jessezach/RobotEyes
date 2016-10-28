from PIL import Image
import subprocess
import os, shutil
from robot.libraries.BuiltIn import BuiltIn


class RobotEyes(object):

    def __init__(self, env, mode):
        self.env = env
        self.mode = mode
        self.count = 1
        self.root_path = os.path.dirname(os.path.abspath(__file__))

    def open_eyes(self):
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

        if self.mode == 'test':
            if os.path.exists(self.root_path + '/actual/' + self.test_name):
                shutil.rmtree(self.root_path + '/actual/' + self.test_name)

            if os.path.exists(self.root_path + '/diff/' + self.test_name):
                shutil.rmtree(self.root_path + '/diff/' + self.test_name)

        elif self.mode == 'baseline':
            if os.path.exists(self.root_path + '/baseline/' + self.test_name):
                shutil.rmtree(self.root_path + '/baseline/' + self.test_name)

        else:
            raise ValueError('Mode should be test or baseline')

    def capture_full_screen(self):
        test_name = self.test_name.replace(' ', '_')

        if self.mode.lower() == 'baseline':
            path = self.root_path + '/baseline/' + test_name

        elif self.mode.lower() == 'test':
            path = self.root_path + '/actual/' + test_name

        if not os.path.exists(path):
            os.makedirs(path)

        print 'Capturing page...'
        self.driver.save_screenshot(path + '/img' + str(self.count) + '.png')
        self.count += 1

    def capture_element(self, selector, value, left=0, top=0,right=0, bottom=0):
        test_name = self.test_name.replace(' ', '_')

        if self.mode.lower() == 'baseline':
            path = self.root_path + '/baseline/' + test_name

        elif self.mode.lower() == 'test':
            path = self.root_path + '/actual/' + test_name

        if selector.upper() == 'XPATH':
            search_element = self.driver.find_element_by_xpath(value)
        elif selector.upper() == 'ID':
            search_element = self.driver.find_element_by_id(value)
        elif selector.upper() == 'CLASS NAME':
            search_element = self.driver.find_element_by_class_name(value)
        elif selector.upper() == 'CSS SELECTOR':
            search_element = self.driver.find_element_by_css_selector(value)

        if not os.path.exists(path):
            os.makedirs(path)

        print 'Capturing element...'
        self.driver.save_screenshot(path + '/img' + str(self.count) + '.png')
        location = search_element.location
        size = search_element.size

        self.driver.save_screenshot(path + '/img' + str(self.count) + '.png')
        im = Image.open(path + '/img' + str(self.count) + '.png')

        l = int(location['x'])
        t = int(location['y'])
        r = int(location['x'] + size['width'])
        b = int(location['y'] + size['height'])
        right = int(right)
        bottom = int(bottom)
        left = int(left)
        top = int(top)
        im = im.crop((left+l, top+t, right+r, bottom+b)) # defines crop points
        im.save(path + '/img' + str(self.count) + '.png')
        self.count += 1

    def compare_images(self):
        if self.env.lower() == 'local' and self.mode.lower() == 'test':
            test_name = self.test_name.replace(' ', '_')
            baseline_path = self.root_path + '/baseline/' + test_name
            actual_path = self.root_path + '/actual/' + test_name
            diff_path = self.root_path + '/diff/' + test_name

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

                    proc = subprocess.Popen('compare -metric RMSE -subimage-search -dissimilarity-threshold 1.0 %s %s %s' % (a_path, b_path, d_path),
                                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                    out, err = proc.communicate()
                    difference = err.split()[1][1:-1]
                    output = open(actual_path + '/' + filename + '.txt', 'a+')
                    output.write(difference)
                    output.close()
