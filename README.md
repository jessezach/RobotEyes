# RobotEyes
Visual Regression Library for Robot Framework

Uses Imagemagick to compare images and create a diff image. Custom Report to view baseline, actual and diff images. View passed and failed tests. Blur regions (only for selenium) within a page to ignore comparison (helpful when there are dynamic elements like text etc in a page). Support SeleniumLibrary(tested) , Selenium2Library(tested) and AppiumLibrary(not tested).

- Import the Library into your Robot test. Pass Mode `test` or `baseline` as an argument. E.g: <br/>    
 ```
    Library    RobotEyes    test
 ```    
- Call the `open eyes` keyword after opening the browser in your selenium test.
- Use the `capture full screen` and `capture element` keywords to capture images.
- Call the `compare images` keyword at the end of the test to compare all the images captured in the respective test.
- Once done running the tests, view test report within the specified result folder or execute the report generator script and pass the path to output directory to generate report manually. Eg:<br/>
```
    reportgen results
``` 
- A custom report will be generated within the specified results folder (or root). 

# Requirements
- Install the `robotframework-eyes` library using `pip`: 
```
    pip install robotframework-eyes
```     
- Install `Imagemagick` (for mac: `brew install imagemagick`, linux: `apt-get install imagemagick`) <br/>

# Example
```
*** Settings ***
Library    Selenium2Library
Library    RobotEyes    test   0.01
# Above, use `baseline` instead of `test`, if running the test case for the very first time. 
# The 3rd argument is the global test tolerance (optional)

*** Variables ***
@{blur}    id=body    css=#SIvCob

*** Test Cases ***    
Sample visual regression test case  # Name of the example test case
    open browser    https://www.google.com/    chrome
    maximize browser window
    open eyes    SeleniumLibrary  # Use the selenium library as the argument E.g. AppiumLibrary or SeleniumLibrary
    wait until element is visible    id=lst-ib
    # Below, the optional arguments are the tolerance to override global value, the regions to blur in the image and
    # the thickness of the blur (radius of Gaussian blur applied to the regions) 
    capture full screen    0.05    ${blur}    50
    capture element    id=hplogo
    compare images
    close browser
```
The report should get generated after test have finished. To generate report manually, run:<br/>
```
    reportgen path/to/output directory
```

# Keyword Documentation
**open eyes** - Arguments: library Eg AppiumLibrary (optional) - (Gets current selenium/appium instance) <br/>
**capture full screen** - Arguments: tolerance, blur (array of locators to blur, optional), radius(thickness of blur, optional) - (Captures an entire page)<br/>
**capture element** - Arguments: locator, blur(array of locators to blur, optional), radius(thickness of blur, optional)(Captures a region or an individual element in a webpage)<br/>
**capture mobile element** - Arguments: locator - (Captures a region or an individual element in a mobile screen)<br/>
**scroll to element** - Arguments: locator - (Scrolls to an element in a webpage)<br/>
**compare images** - Arguments: None - (Compares baseline and actual images of a testcase)<br/>

# Note: 
If you find this library useful, please do star the repository. 
For any issue, feature request or clarification feel free to raise an issue in github or email me at iamjess988@gmail.com
