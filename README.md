# RobotEyes
Visual Regression Library for Robot Framework

Uses Imagemagick to compare images and create a diff image. Also contains a report generator to create a custom
visual test report.

- Place the files in the "Lib" folder of your Robot project.
- Import the Library into your Robot test. Pass ENV("local") Mode("test" or "baseline") as arguments.
- Call open eyes method to after opening the browser in your selenium test.
- Use the capture full screen, capture element keywords to capture images.
- Call the compare images keyword at the end of the test to compare all the images captured in the respective test.
- Once done running the tests, execute the report generator script and pass the path to output.xml as argument from commandline.
A custom report will be generated at the root of your project. 
It will display the baseline, actual and diff images along with the diff value.

