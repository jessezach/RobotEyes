from setuptools import setup, find_packages
import os

version = '1.3.2'

setup(name='robotframework-eyes',
      version=version,
      description="Visual regression library and report generator for robot framework",
      long_description="""\
Visual regression library and report generator for robot framework. Capture elements, fullscreens and compare them against baseline images. Extends Selenium2Libary. Visit https://github.com/jz-jess/RobotEyes for documentation.""",
      classifiers=[
        'Framework :: Robot Framework',
        'Programming Language :: Python',
        'Topic :: Software Development :: Testing',
      ],
      keywords='visual-regression image-comparison robotframework robot-eyes',
      author='Jesse Zacharias',
      author_email='iamjess988@gmail.com',
      url='https://github.com/jz-jess/RobotEyes',
      license='MIT',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'pillow',
          'robotframework',
          'flask'
      ],
      entry_points={
          'console_scripts': [
              'eyes = RobotEyes.runner:main',
              'reportgen = RobotEyes.reportgen:report_gen'
          ]
      },
)
