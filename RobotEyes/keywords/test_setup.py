import os

from PIL import Image
from robot.libraries.BuiltIn import BuiltIn

from ..constants import *
from ..selenium_hooks import SeleniumHooks
from ..utils import Utils


class SetupKeywords(object):
    def open_eyes(
        self,
        lib='SeleniumLibrary',
        tolerance=0,
        template_id=None,
        cleanup=None
    ):
        self._set_options(lib, tolerance, template_id, cleanup)

    def _set_cleanup(self, cleanup):
        self.cleanup_files = None
        if cleanup in CLEANUP_OPTIONS:
            self.cleanup_files = cleanup

    def _delete_folder_if_exists(self):
        actual_image_test_folder = os.path.join(
                                       self.images_base_folder,
                                       ACTUAL_IMAGE_BASE_FOLDER,
                                       self.test_name_folder
                                   )
        diff_image_test_folder = os.path.join(
                                     self.images_base_folder,
                                     DIFF_IMAGE_BASE_FOLDER,
                                     self.test_name_folder
                                  )
        Utils.cleanup_files([actual_image_test_folder, diff_image_test_folder])

    def _create_empty_folder(self):
        if self.lib.lower() != 'none':
            self.path = os.path.join(self.baseline_dir, self.test_name_folder)

            if not os.path.exists(self.path):
                os.makedirs(self.path)

        self.path = os.path.join(self.images_base_folder, ACTUAL_IMAGE_BASE_FOLDER, self.test_name_folder)

        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def _output_dir(self):
        output_dir = self._get_variable_value('${OUTPUT DIR}')

        if 'pabot_results' in output_dir:
            index = output_dir.find(os.path.sep + 'pabot_results')
            return output_dir[:index]
        return output_dir

    def _get_baseline_dir(self):
        baseline_dir = self._get_variable_value('${images_dir}')
        if not baseline_dir:
            BuiltIn().run_keyword('Fail', 'Please provide image baseline directory. Ex: -v images_dir:base')

        os.makedirs(baseline_dir) if not os.path.exists(baseline_dir) else ''
        return baseline_dir

    def _get_actual_dir(self):
        return self._get_variable_value('${actual_dir}')

    @staticmethod
    def _get_variable_value(var):
        return BuiltIn().get_variable_value(var)

    def _get_name(self):
        return 'img%s' % str(self.count)

    def _get_tolerance(self, tolerance):
        if tolerance:
            tolerance = float(tolerance)
        else:
            tolerance = self.tolerance

        if tolerance >= 1:
            tolerance = tolerance/100.0
        return tolerance

    def _set_tolerance(self, tolerance):
        self.tolerance = float(tolerance or 0)

        if self.tolerance >= 1:
            self.tolerance = self.tolerance/100

    def _set_directories(self):
        self.baseline_dir = self._get_baseline_dir()
        self.actual_dir = self._get_actual_dir()
        self.output_dir = self._output_dir()
        self.images_base_folder = os.path.join(self.output_dir, IMAGES_FOLDER)

    def _set_test_options(self, lib, template_id):
        self.lib = lib or 'SeleniumLibrary'
        self.stats = {}
        self.fail = False
        if self.lib.lower() != 'none':
            self.browser = SeleniumHooks(self.lib)

        if template_id:
            self.test_name += '_%s' % template_id

        self.test_name = self._get_variable_value('${TEST NAME}')
        self.test_name_folder = self.test_name.replace(' ', '_')
        print("roboteyestestfolder: %s" % self.test_name_folder)
        self._initialise_directories()
        self.pass_color = 'green'
        self.fail_color = 'red'
        self.count = 1

    def _set_options(self, lib, tolerance, template_id, cleanup):
        self._set_cleanup(cleanup)
        self._set_tolerance(tolerance)
        self._set_directories()
        self._set_test_options(lib, template_id)

    def _initialise_directories(self):
        # delete if directory already exist. Fresh test
        self._delete_folder_if_exists()
        # recreate deleted folder
        self._create_empty_folder()