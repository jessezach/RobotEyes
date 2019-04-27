# RobotEyes
[![Downloads](https://pepy.tech/badge/robotframework-eyes)](https://pepy.tech/project/robotframework-eyes)
[![Version](https://img.shields.io/pypi/v/robotframework-eyes.svg)](https://pypi.org/project/robotframework-eyes)
[![HitCount](http://hits.dwyl.io/jz-jess/RobotEyes.svg)](http://hits.dwyl.io/jz-jess/RobotEyes)<br/>

Visual Regression Library for Robot Framework

Uses Imagemagick to Compare Images and create a diff image. Custom Report to view baseline, actual and diff images. View passed and failed tests. Blur regions (only for selenium) within a page to ignore comparison (helpful when there are dynamic elements like text etc in a page). Support SeleniumLibrary(tested) , Selenium2Library(tested) and AppiumLibrary(not tested).
## Requirements
- Install the `robotframework-eyes` library using `pip`: 
```
    pip install robotframework-eyes
```     
- Install `Imagemagick 6.x` (for mac: `brew install imagemagick`, linux: `apt-get install imagemagick`) <br/>
-- **Important**: make sure that you check the _Install Legacy Utilities (e.g. convert)_ check mark in the installation process and that the directory to ImageMagick is in your PATH env variable. 
## Quick-reference Usage Guide
- Import the Library into your Robot test. E.g: <br/>    
 ```
    Library    RobotEyes
 ```    
- Call the `Open Eyes` keyword after opening the browser in your selenium test.
- Use the `Capture Full Screen` and `Capture Element` keywords to capture images.
- Call the `Compare Images` keyword at the end of the test to compare all the images captured in the respective test.
- Once done running the tests, view the test report within the specified results folder or execute the report generator script and pass the path to output directory to generate report manually. Eg:<br/>
```
    reportgen --baseline=<baseline image directory> --results=<output directory>
``` 
- A custom report will be generated within the specified results folder (or root). 
## Usage Guide
This guide contains the suggested steps to efficently integrate `RobotEyes` library into your Robot Framework test development workflow.<br/>
It also serves as documentation to clarify how this library functions on a high level.

## Keyword Documentation
- `Open Eyes`:<br/>
Arguments: library. E.g. AppiumLibrary (optional).<br/> 
Gets current selenium/appium instance.<br/>

- `Capture Full Screen`:<br/>
Arguments: tolerance, blur (array of locators to blur, optional), radius(thickness of blur, optional).<br/>
Captures the entire screen.<br/>

- `Capture Element`:<br/>
Arguments: locator, blur(array of locators to blur, optional), radius(thickness of blur, optional).<br/>
Captures a region or an individual element in a webpage.<br/>

- `Capture Mobile Element`:<br/>
Arguments: locator.<br/>
Captures a region or an individual element in a mobile screen.<br/>

- `Scroll To Element`:<br/>
Arguments: locator.<br/>
Scrolls to an element in a webpage.<br/>

- `Compare Images`:<br/>
Arguments: None<br/>
Compares **all** the `actual` images of a test case against the `baseline` images<br/>
### Running Tests ###
`robot -d results -v images_dir:<baseline_images_directory> tests`<br/>
If baseline image directory does not exist, RobotEyes will create it.
If baseline image(s) does not exist, RobotEyes will move the captured image into the baseline directory.
For example, when running tests the first time all captured images will be moved to baseline directory passed by you (images_dir) <br/>
**Important** It is mandatory to pass baseline image directory, absence of which will throw and exception.<br/>

### Directory structure  
The `RobotEyes` library creates a `visual_images` directory which will contain two additional directories, named `actual` & `diff`, respectively.<br/>
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
Baseline images will be generated when tests are run the first time. Subsequent test runs will trigger comparison of actual and baseline images.

For example:
```robotframework
*** Settings ***
Library    Selenium2Library
Library    RobotEyes    5 (tolerance ranging between 1 to 100)

*** Test Cases ***    
Sample visual regression test case  # Name of the example test case
    Open Browser    https://www.google.com/    chrome
    Maximize Browser Window
    Open Eyes    SeleniumLibrary  # Use the selenium library as the argument E.g. AppiumLibrary or SeleniumLibrary
    Wait Until Element Is Visible    id=lst-ib
    Capture Full Screen
    Compare Images
    Close Browser
```
### Comparing the images
To compare the images, the following needs to exist in the TC's code:
- Library declaration:
```robotframework
Library    RobotEyes    5
```
- The `Open Eyes` keyword after the `Open Browser` keyword.
- Any of the image capture keywords. E.g `Capture Full Screen`
- The `Compare Images` keyword after capturing the desired images.

For Example:
```robotframework
*** Settings ***
Library    Selenium2Library
Library    RobotEyes    5

*** Test Cases ***    
Sample visual regression test case  # Name of the example test case
    Open Browser    https://www.google.com/    chrome
    Maximize Browser Window
    Open Eyes    SeleniumLibrary  # Use the selenium library as the argument E.g. AppiumLibrary or SeleniumLibrary
    Wait Until Element Is Visible    id=lst-ib
    Capture Full Screen
    Compare Images
    Close Browser
```
After the comparison is completed (i.e. the `Compare Images` keyword in the TC is executed), a difference image will be generated and stored in the `diff` directory.<br/>
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
Library    RobotEyes    5
# The 2nd argument is the global test tolerance (optional)

*** Variables ***
@{blur}    id=body    css=#SIvCob

*** Test Cases ***    
Sample visual regression test case  # Name of the example test case
    Open Browser    https://www.google.com/    chrome
    Maximize Browser Window
    Open Eyes    SeleniumLibrary  # Use the selenium library as the argument E.g. AppiumLibrary or SeleniumLibrary
    Wait Until Element Is Visible    id=lst-ib
    # Below, the optional arguments are the tolerance to override global value, the regions to blur in the image and
    # the thickness of the blur (radius of Gaussian blur applied to the regions) 
    Capture Full Screen    10(tolerance)    ${blur}    50
    Capture Element    id=hplogo
    Compare Images
    Close Browser
```
## Tolerance
Tolerance is the allowed dissimilarity between images. If comparison difference is more than tolerance, the test fails.<br/>
You can pass tolerance globally at the time of importing RobotEyes. Ex `Library RobotEyes 5`.<br/>
Additionally you can override globaly tolerance by passing it to `Captur Element`, `Capture Fullscreen` keywords.<br/>
Ex: `Capture Element  <locator>  tolerance=10  blur=id=test`<br/>
Tolerance should range between 1 to 10.<br/>

## Blurring elements from image
You can also blur out unwanted elements (dynamic texts etc) from image to ignore them from comparison. This can help in getting more accurate test results. You can pass a list of locators or a single locator as argument to `Capture Element` and `Capture Full Screen` keywords.<br/>
Ex: `Capture Element  <locator>  blur=id=test`
```
    @{blur}    id=body    css=#SIvCob
    Capture Full Screen   <locator>  blur=${blur}
```
## Interactive Report
Robot Eyes generates a report automatically after all tests have been executed. However a more interactive and intuitive flask based report is available.<br/>

You can view passed and failed tests and also use this feature to move acceptable actual images to baseline directory.
Run eyes server like this. `eyes --baseline=<baseline image directory> --results=<outputdir>(leave empty if output is at project root)`

## Pabot users
Visual tests can be executed in parallel using pabot. However there may be issues with the auto-generated report after the tests have finished.
A workaround can be to generate the report using `reportgen` to ensure it has no discrepancies.

## Contributors:
[Adirala Shiva](https://github.com/adiralashiva8) Contributed in creating a robotmetrics inspired reporting for RobotEyes.</br>
[DiegoSanchezE](https://github.com/DiegoSanchezE) Added major improvements in the ReadMe.

## Note
If you find this library useful, please do star the repository.<br/> 
For any issue, feature request or clarification feel free to raise an issue in github or email me at iamjess988@gmail.com
