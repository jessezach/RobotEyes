# RobotEyes
[![Downloads](https://pepy.tech/badge/robotframework-eyes)](https://pepy.tech/project/robotframework-eyes)
[![Version](https://img.shields.io/pypi/v/robotframework-eyes.svg)](https://pypi.org/project/robotframework-eyes)
[![HitCount](http://hits.dwyl.io/jz-jess/RobotEyes.svg)](http://hits.dwyl.io/jz-jess/RobotEyes)<br/>

Visual Regression Library for Robot Framework

Uses Imagemagick to compare images and create a diff image. Custom Report to view baseline, actual and diff images. View passed and failed tests. Blur regions (only for selenium) within a page to ignore comparison (helpful when there are dynamic elements like text etc in a page). Support SeleniumLibrary(tested) , Selenium2Library(tested) and AppiumLibrary(not tested).
## Requirements
- Install the `robotframework-eyes` library using `pip`: 
```
    pip install robotframework-eyes
```     
- Install `Imagemagick` (for mac: `brew install imagemagick`, linux: `apt-get install imagemagick`) <br/>
-- **Important**: make sure that you check the _Install Legacy Utilities (e.g. convert)_ check mark in the installation process and that the directory to ImageMagick is in your PATH env variable. 
## Quick-reference Usage Guide
- Import the Library into your Robot test. Pass Mode `test` or `baseline` as an argument. E.g: <br/>    
 ```
    Library    RobotEyes    test
 ```    
- Call the `open eyes` keyword after opening the browser in your selenium test.
- Use the `capture full screen` and `capture element` keywords to capture images.
- Call the `compare images` keyword at the end of the test to compare all the images captured in the respective test.
- Once done running the tests, view the test report within the specified results folder or execute the report generator script and pass the path to output directory to generate report manually. Eg:<br/>
```
    reportgen results
``` 
- A custom report will be generated within the specified results folder (or root). 
## Usage Guide
This guide contains the suggested steps to efficently integrate `RobotEyes` library into your Robot Framework test development workflow.<br/>
It also serves as documentation to clarify how this library functions on a high level.

## Keyword Documentation
- `open eyes`:<br/>
Arguments: library. E.g. AppiumLibrary (optional).<br/> 
Gets current selenium/appium instance.<br/>

- `capture full screen`:<br/>
Arguments: tolerance, blur (array of locators to blur, optional), radius(thickness of blur, optional).<br/>
Captures the entire screen.<br/>

- `capture element`:<br/>
Arguments: locator, blur(array of locators to blur, optional), radius(thickness of blur, optional).<br/>
Captures a region or an individual element in a webpage.<br/>

- `capture mobile element`:<br/>
Arguments: locator.<br/>
Captures a region or an individual element in a mobile screen.<br/>

- `scroll to element`:<br/>
Arguments: locator.<br/>
Scrolls to an element in a webpage.<br/>

- `compare images`:<br/>
Arguments: None<br/>
Compares **all** the `actual` images of a test case against the `baseline` images<br/>

### Directory structure  
The `RobotEyes` library creates a `visual_images` directory which will contain three additional directories, named `baseline`, `actual` & `diff`, respectively.<br/>
These directories are necessary for the library to function and are created by it at different stages of the test case (TC) development workflow.<br/>
The resulting directory structure created in the project looks as follows:

<div>
  <ul class="ascii">
    <li>visual_images/
      <ul>
        <li>actual/
          <ul>
            <li>name_of_tc1/
              <ul>
                <li>img1.png</li>
                <li>img1.png.txt</li>
              </ul>
            </li>
            <li>name_of_tc2/
              <ul>
                <li>img1.png</li>
                <li>img1.png.txt</li>
              </ul>
            </li>
            <li>name_of_tc3/
              <ul>
                <li>img1.png</li>
                <li>img1.png.txt</li>
              </ul> 
            </li>
          </ul>
        </li>
        <li>baseline/
          <ul>
            <li>name_of_tc1/
              <ul>
                <li>img1.png</li>
              </ul>
            </li>
            <li>name_of_tc2/
              <ul>
                <li>img1.png</li>
              </ul>
            </li>
            <li>name_of_tc3/
              <ul>
                <li>img1.png</li>
              </ul>
            </li>
          </ul>
        </li>
        <li>diff/
          <ul>
            <li>name_of_tc1/
              <ul>
                <li>img1.png</li>
              </ul>
            </li>
            <li>name_of_tc2/
              <ul>
                <li>img1.png</li>
              </ul>
            </li>
            <li>name_of_tc3/
              <ul>
                <li>img1.png</li>
              </ul>
            </li>
          </ul>
        </li>
      </ul>
    </li>
  </ul>  
</div>

### Generating the baseline images
To generate the `baseline` images against which the `actual` images will be compared, the following lines of code need to be in the Robot Framework TC file:
- Library declaration:
```robotframework
    Library    RobotEyes    baseline    0.01
```
- The `open eyes` keyword after the `open browser` keyword.
- Any of the image capture keywords. E.g `capture full screen`

For example:
```robotframework
*** Settings ***
Library    Selenium2Library
Library    RobotEyes    baseline    0.01
# Above, use `baseline` instead of `test`, if running the test case for the very first time. 
# The 3rd argument is the global test tolerance (optional)

*** Test Cases ***    
Sample visual regression test case  # Name of the example test case
    open browser    https://www.google.com/    chrome
    maximize browser window
    open eyes    SeleniumLibrary  # Use the selenium library as the argument E.g. AppiumLibrary or SeleniumLibrary
    wait until element is visible    id=lst-ib
    capture full screen
    close browser
```

If the test above is executed, `RobotEyes` will take a full screen capture, name it `img1.png` and store it in the `baseline` directory.<br/>
This image will be used to compare while in `test` mode (instead of `baseline` mode) later on.<br/>
If more "capture" keywords are in the TC, the quantity and name of the `baseline` images will increase accordingly (i.e. `img1.png`, `img2.png`, ... `imgN.png`).<br/>
If the TC is executed again in `baseline` mode, the `baseline` images will be recaptured and those will overwrite the previous ones.<br/>

### Generating the actual images
Similarly, to generate the `actual` images, the following needs to exist in the code:
- Library declaration:
```robotframework
Library    RobotEyes    test    0.01
```
- The `open eyes` keyword after the `open browser` keyword.
- Any of the image capture keywords. E.g `capture full screen`

For example:
```robotframework
*** Settings ***
Library    Selenium2Library
Library    RobotEyes    test    0.01
# Above, use `baseline` instead of `test`, if running the test case for the very first time. 
# The 3rd argument is the global test tolerance (optional)

*** Test Cases ***    
Sample visual regression test case  # Name of the example test case
    open browser    https://www.google.com/    chrome
    maximize browser window
    open eyes    SeleniumLibrary  # Use the selenium library as the argument E.g. AppiumLibrary or SeleniumLibrary
    wait until element is visible    id=lst-ib
    capture full screen
    close browser
```
Notice that the only difference is that the library declaration argument changed from `baseline` to `test`.<br/>
If the TC above is executed, the library will use the same capture keyword to generate the `actual` image, which will also be named `img1.png`.<br/>
Here, more capture keywords also mean more images in the `actual` directory.

### Comparing the images
To compare the images, the following needs to exist in the TC's code:
- Library declaration:
```robotframework
Library    RobotEyes    test    0.01
```
- The `open eyes` keyword after the `open browser` keyword.
- Any of the image capture keywords. E.g `capture full screen`
- The `compare images` keyword after capturing the desired images.

For Example:
```robotframework
*** Settings ***
Library    Selenium2Library
Library    RobotEyes    test    0.01
# Above, use `baseline` instead of `test`, if running the test case for the very first time. 
# The 3rd argument is the global test tolerance (optional)

*** Test Cases ***    
Sample visual regression test case  # Name of the example test case
    open browser    https://www.google.com/    chrome
    maximize browser window
    open eyes    SeleniumLibrary  # Use the selenium library as the argument E.g. AppiumLibrary or SeleniumLibrary
    wait until element is visible    id=lst-ib
    capture full screen
    compare images
    close browser
```
After the comparison is completed (i.e. the `compare images` keyword in the TC is executed), a difference image will be generated and stored in the `diff` directory.<br/>
Also, a text file will be created containing the result of the comparison between the RMSE (root mean squared error) of the `diff` image and the tolerance set by the user.<br/>
After that, the regular Robot Framework report will raise a failure if the comparison fails.
Additionally, the visual report should automatically be generated after test have finished.<br/>
To generate visual report manually, run:<br/>
```
    reportgen path/to/output directory
```

### Another test example
```robotframework
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

## Pabot users
Visual tests can be executed in parallel using pabot. However there may be issues with the auto-generated report after the tests have finished.
A workaround can be to generate the report using `reportgen` to ensure it has no discrepancies.

## Note
If you find this library useful, please do star the repository.<br/> 
For any issue, feature request or clarification feel free to raise an issue in github or email me at iamjess988@gmail.com
