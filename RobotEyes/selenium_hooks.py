import math
import platform

from PIL import Image, ImageFilter
from robot.libraries.BuiltIn import BuiltIn
from selenium.common.exceptions import JavascriptException
from selenium.common.exceptions import NoSuchElementException


class SeleniumHooks(object):
    count = 0
    mobile = False

    def __init__(self, lib):
        try:
            s2l = BuiltIn().get_library_instance(lib)
            if lib == 'AppiumLibrary':
                self.driver = s2l._current_application()
                self.mobile = True
            else:
                try:
                    self.driver = s2l.driver #SeleniumLibrary v4
                except:
                    self.driver = s2l._current_browser() #SeleniumLibrary v4--
        except RuntimeError:
            raise Exception('%s instance not found' % lib)

    def is_mobile(self):
        return self.mobile

    def capture_full_screen(self, path, blur=[], radius=50):
        self.count += 1
        self.driver.save_screenshot(path + '/img' + str(self.count) + '.png')
        if blur:
            initial_frame = self.driver.execute_script("return window.frameElement")
            self.blur_regions(blur, radius, path)
            self.driver.switch_to.default_content()
            self.blur_in_all_frames(blur, radius, path)
            self.driver.switch_to.default_content()
            print("Switching back to initial frame and name is %s" % initial_frame)
            self.driver.switch_to.frame(initial_frame)

        return self.count

    def blur_in_all_frames(self, blur, radius, path):
        frames = self.driver.find_elements_by_tag_name("frame")
        iframes = self.driver.find_elements_by_tag_name("iframe")
        joined_list = frames + iframes
        print("Frames: %s" % str(len(joined_list)))
        for index, frame in enumerate(joined_list):
            print("Switching to Frame %s" % frame)
            self.driver.switch_to.frame(frame)
            self.blur_regions(blur, radius, path)
            self.driver.switch_to.default_content()

    def capture_element(self, path, locator, blur=[], radius=50):
        self.count += 1
        self.driver.save_screenshot(path + '/img' + str(self.count) + '.png')
        prefix, locator, element = self.find_element(locator)
        coord = self._get_coordinates(prefix, locator, element)
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

    def capture_mobile_element(self, selector, path, blur=[], radius=50):
        self.count += 1
        prefix, locator, search_element = self.find_element(selector)
        location = search_element.location
        size = search_element.size
        self.driver.save_screenshot(path + '/img' + str(self.count) + '.png')
        left = location['x']
        top = location['y']
        right = location['x'] + size['width']
        bottom = location['y'] + size['height']
        self.blur_regions(blur, radius, path) if blur else ''
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
            try:
                prefix, locator, element = self.find_element(region)
            except NoSuchElementException:
                continue

            area_coordinates = self._get_coordinates_from_driver(element)
            frame_abs_pos = self._get_current_frame_abs_position()
            left, right = math.ceil(area_coordinates['left'] + frame_abs_pos['x']), math.ceil(area_coordinates['right'] + frame_abs_pos['x'])
            top, bottom = math.ceil(area_coordinates['top'] + frame_abs_pos['y']), math.ceil(area_coordinates['bottom'] + frame_abs_pos['y'])
            left, right, top, bottom = self._update_coordinates(left, right, top, bottom)
            im = Image.open(path + '/img' + str(self.count) + '.png')
            cropped_image = im.crop((left, top, right, bottom))
            blurred_image = cropped_image.filter(ImageFilter.GaussianBlur(radius=int(radius)))
            im.paste(blurred_image, (left, top, right, bottom))
            im.save(path + '/img' + str(self.count) + '.png')

    def _get_current_frame_abs_position(self):
        cmd = 'function currentFrameAbsolutePosition() { \
        let currentWindow = window; \
        let currentParentWindow; \
        let positions = []; \
        let rect;  \
        while (currentWindow !== window.top) { \
            currentParentWindow = currentWindow.parent; \
            for (let idx = 0; idx < currentParentWindow.frames.length; idx++) { \
                if (currentParentWindow.frames[idx] === currentWindow) { \
                    for (let frameElement of currentParentWindow.document.getElementsByTagName("frame")) { \
                        if (frameElement.contentWindow === currentWindow) { \
                            rect = frameElement.getBoundingClientRect(); \
                            positions.push({x: rect.x, y: rect.y}); \
                        } \
                    } \
                    for (let frameElement of currentParentWindow.document.getElementsByTagName("iframe")) { \
                        if (frameElement.contentWindow === currentWindow) { \
                            rect = frameElement.getBoundingClientRect(); \
                            positions.push({x: rect.x, y: rect.y}); \
                        } \
                    } \
                    currentWindow = currentParentWindow; \
                    break; \
                } \
            } \
        } \
        return positions.reduce((accumulator, currentValue) => { \
            return { \
            x: accumulator.x + currentValue.x, \
            y: accumulator.y + currentValue.y \
            }; \
        }, { x: 0, y: 0 }); \
        }; return currentFrameAbsolutePosition();'

        try:
            coordinates = self.driver.execute_script(cmd)
        except JavascriptException:
            coordinates = {"x": 0, "y": 0}
        return coordinates

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

    def _get_coordinates(self, prefix, locator, element):
        if self.mobile:
            coordinates = self._get_coordinates_from_driver(element)
        else:
            if prefix.lower() == 'xpath':
                locator = locator.replace('"', "'")
                cmd = "var e = document.evaluate(\"{0}\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null)" \
                      ".singleNodeValue;return e.getBoundingClientRect();".format(locator)

            elif prefix.lower() == 'css':
                locator = locator.replace('"', "'")
                cmd = "var e = document.querySelector(\"{0}\");return e.getBoundingClientRect();".format(locator)

            elif prefix.lower() == 'id':
                cmd = "var e = document.getElementById(\"{0}\");return e.getBoundingClientRect();".format(locator)

            elif prefix.lower() == 'class':
                cmd = "var e = document.getElementsByClassName(\"{0}\")[0];return e.getBoundingClientRect();" \
                    .format(locator)
            else:
                raise Exception('Invalid locator %s' % locator)

            try:
                coordinates = self.driver.execute_script(cmd)
            except JavascriptException:
                coordinates = self._get_coordinates_from_driver(element)
            
        return coordinates

    def _get_coordinates_from_driver(self, element):
        coordinates = {}
        location = element.location
        size = element.size
        coordinates['left'] = location['x']
        coordinates['top'] = location['y']
        coordinates['right'] = location['x'] + size['width']
        coordinates['bottom'] = location['y'] + size['height']
        return coordinates

    def _update_coordinates(self, left, right, top, bottom):
        if platform.system().lower() == "darwin":
            left = left * 2
            right = right * 2
            top = top * 2
            bottom = bottom * 2
        return int(left), int(right), int(top), int(bottom)