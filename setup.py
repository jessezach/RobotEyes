from setuptools import setup, find_packages
import sys, os

version = '0.3'

setup(name='robotframework-eyes',
      version=version,
      description="Visual regression library and report generator for robot framework",
      long_description="""\
Visual regression library and report generator for robot framework. Capture elements, fullscreens and compare them against baseline images. Works for mobile. Extends selenium and appium. Dependent on selenium2library and appiumLibrary along with r robot framework""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='visual-regression image-comparison roboteyes',
      author='Jesse Zacharias',
      author_email='iamjess988@gmail.com',
      url='',
      scripts=[os.path.join('scripts', 'reportgen')],
      license='BSD',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'pillow',
          'robotframework',
          'robotframework-selenium2library'
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
