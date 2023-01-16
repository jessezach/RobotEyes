import os
import shutil

from robot.libraries.BuiltIn import BuiltIn

from ..constants import *
from ..imagemagick import Imagemagick
from ..utils import Utils


class CompareKeywords(object):
    def compare_images(self):
        baseline_path, actual_path, diff_path = self._get_all_paths()
        if not os.path.exists(diff_path):
            os.makedirs(diff_path)

        # compare actual and baseline images and save the diff image
        for filename in os.listdir(actual_path):
            if filename.endswith('.png'):
                b_path, a_path, d_path, output_path = self._get_image_paths(
                                                        baseline_path,
                                                        actual_path,
                                                        diff_path,
                                                        filename)
                self._compare_and_write_result(b_path, a_path, d_path, filename, output_path)

        if self.fail:
            BuiltIn().run_keyword('Fail', 'Image dissimilarity exceeds tolerance')
        elif self.cleanup_files:
            self._cleanup_passed(actual_path, diff_path)

    def compare_two_images(self, ref, actual, output, tolerance=None):
        ref += '.png' if ref.split('.')[-1] not in IMAGE_EXTENSIONS else ''
        actual += '.png' if actual.split('.')[-1] not in IMAGE_EXTENSIONS else ''
        output += '.png' if output.split('.')[-1] not in IMAGE_EXTENSIONS else ''
        tolerance = float(tolerance) if tolerance else self.tolerance
        tolerance = tolerance / 100 if tolerance >= 1 else tolerance

        if not ref or not actual:
            raise Exception('Please provide reference and actual image names')

        first_path = os.path.join(self.baseline_dir, ref)
        second_path = os.path.join(self.actual_dir, actual)

        if os.path.exists(first_path) and os.path.exists(second_path):
            diff_path = os.path.join(self.path, output)
            difference = Imagemagick(first_path, second_path, diff_path).compare_images()
            color, result = self._get_result(difference, tolerance)
            self.stats[output] = tolerance
            text = '%s %s' % (result, color)
            txt_path = os.path.join(self.path, output + '.txt')
            outfile = open(txt_path, 'w')
            outfile.write(text)
            outfile.write("\n")
            img_names = '%s %s' % (ref, actual)
            outfile.write(img_names)
            outfile.close()
            if color == self.pass_color and self.cleanup_files:
                self._cleanup_passed(self.actual_dir, diff_path)
        else:
            raise Exception('Image %s or %s doesnt exist' % (ref, actual))

    def _compare_and_write_result(self, b_path, a_path, d_path, filename, output_path):
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
            color = self.pass_color
            text = '%s %s' % ('None', color)
        self._write_result(output_path, text)

    @staticmethod
    def _write_result(path, text):
        output = open(path, 'w')
        output.write(text)
        output.close()

    def _get_all_paths(self):
        test_name = self.test_name.replace(' ', '_')
        baseline_path = os.path.join(self.baseline_dir, test_name)
        actual_path = os.path.join(self.images_base_folder, ACTUAL_IMAGE_BASE_FOLDER, test_name)
        diff_path = os.path.join(self.images_base_folder, DIFF_IMAGE_BASE_FOLDER, test_name)
        return baseline_path, actual_path, diff_path

    @staticmethod
    def _get_image_paths(
        baseline_path,
        actual_path,
        diff_path,
        filename
    ):
        b_path = os.path.join(baseline_path, filename)
        a_path = os.path.join(actual_path, filename)
        d_path = os.path.join(diff_path, filename)
        txt_path = os.path.join(actual_path, filename + '.txt')
        return b_path, a_path, d_path, txt_path

    def _get_result(self, difference, threshold):
        difference, threshold = float(difference * 100), float(threshold * 100)
        if difference > threshold:
            color = self.fail_color
            result = '%s<%s' % (threshold, difference)
            self.fail = True
        elif difference == threshold:
            color = self.pass_color
            result = '%s==%s' % (threshold, difference)
        else:
            color = self.pass_color
            result = '%s>%s' % (threshold, difference)
        return color, result

    def _cleanup_passed(self, actuals_path, diff_path):
        if self.cleanup_files == 'diffs_passed':
            Utils.cleanup_files([diff_path])
        elif self.cleanup_files == 'actuals_passed':
            Utils.cleanup_files([actuals_path])
        else:
            Utils.cleanup_files([diff_path, actuals_path])
