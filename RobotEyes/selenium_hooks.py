import math
import platform

from PIL import Image, ImageFilter
from robot.libraries.BuiltIn import BuiltIn


class SeleniumHooks(object):
    count = 0

    def __init__(self, lib):
        try:
            s2l = BuiltIn().get_library_instance(lib)
            self.driver = s2l._current_application() if lib == 'AppiumLibrary' else s2l._current_browser()
        except RuntimeError:
            raise Exception('%s instance not found' % lib)

    def capture_full_screen(self, path, blur=[], radius=50):
        self.count += 1
        self.driver.save_screenshot(path + '/img' + str(self.count) + '.png')
        self.blur_regions(blur, radius, path) if blur else ''
        return self.count

    def capture_element(self, path, locator, blur=[], radius=50):
        self.count += 1
        self.driver.save_screenshot(path + '/img' + str(self.count) + '.png')
        prefix, locator, _ = self.find_element(locator)
        coord = self._get_coordinates(prefix, locator)
        left, right, top, bottom = self._update_coordinates(
            math.ceil(coord['left']),
            math.ceil(coord['right']),
            math.ceil(coord['top']),
            math.ceil(coord['bottom'])
        )
        self.blur_regions(blur, radius, path) if blur else ''
        im = Image.open(path + '/img' + str(self.count) + '.png')
        im = im.crop((left, top, right, bottom))
        im.resize((1024, 700), Image.ANTIALIAS)
        im.save(path + '/img' + str(self.count) + '.png')
        return self.count

    def capture_mobile_element(self, selector, path):
        self.count += 1
        prefix, locator, search_element = self.find_element(selector)
        location = search_element.location
        size = search_element.size
        self.driver.save_screenshot(path + '/img' + str(self.count) + '.png')
        left = location['x']
        top = location['y']
        right = location['x'] + size['width']
        bottom = location['y'] + size['height']
        image = Image.open(path + '/img' + str(self.count) + '.png')
        image = image.crop((left, top, right, bottom))
        image.save(path + '/img' + str(self.count) + '.png')
        return self.count

    def scroll_to_element(self, selector):
        prefix, locator, search_element = self.find_element(selector)
        self.driver.execute_script("return arguments[0].scrollIntoView();", search_element)

    def blur_regions(self, selectors, radius, path):
        selectors = selectors if isinstance(selectors, list) else [selectors]

        for region in selectors:
            prefix, locator, _ = self.find_element(region)
            area_coordinates = self._get_coordinates(prefix, locator)
            left, right = math.ceil(area_coordinates['left']), math.ceil(area_coordinates['right'])
            top, bottom = math.ceil(area_coordinates['top']), math.ceil(area_coordinates['bottom'])
            left, right, top, bottom = self._update_coordinates(left, right, top, bottom)
            im = Image.open(path + '/img' + str(self.count) + '.png')
            cropped_image = im.crop((left, top, right, bottom))
            blurred_image = cropped_image.filter(ImageFilter.GaussianBlur(radius=int(radius)))
            im.paste(blurred_image, (left, top, right, bottom))
            im.save(path + '/img' + str(self.count) + '.png')

    def find_element(self, selector):
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

    def _update_coordinates(self, left, right, top, bottom):
        if platform.system().lower() == "darwin":
            left = left * 2
            right = right * 2
            top = top * 2
            bottom = bottom * 2
        return int(left), int(right), int(top), int(bottom)
