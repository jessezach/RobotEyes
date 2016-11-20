# RobotEyes
Visual Regression Library for Robot Framework

Uses Imagemagick to compare images and create a diff image. Also contains a report generator to create a custom
visual test report.

- Import the Library into your Robot test. Pass Mode("test" or "baseline") as argument.
- Call open eyes method after opening the browser in your selenium test.
- Use the capture full screen, capture element keywords to capture images.
- Call the compare images keyword at the end of the test to compare all the images captured in the respective test.
- Once done running the tests, execute the report generator script and pass the path to output directory .Eg reportgen results
- A custom report will be generated at the root of your project. 
- It will display the baseline images if run on "baseline" mode. Baseline, Actual and diff in "test" mode.

Example:
Library  Selenium2Library
Library  RobotEyes  test (or baseline, if running for the first time)


*** Test Cases ***
Sample visual regression test case
	open browser  https://www.google.com/  chrome
	maximize browser window
	open eyes
	wait until element is visible  id=lst-ib
	capture full screen
	capture element  id=hplogo
	compare images
	close browser

To generate the report:
reportgen /path/to/output directory
