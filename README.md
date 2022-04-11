# RobotEyes
[![Downloads](https://pepy.tech/badge/robotframework-eyes)](https://pepy.tech/project/robotframework-eyes)
[![Version](https://img.shields.io/pypi/v/robotframework-eyes.svg)](https://pypi.org/project/robotframework-eyes)

Visual Regression Library for Robot Framework

Uses Imagemagick to Compare Images and create a diff image. Custom Report to view baseline, actual and diff images. View passed and failed tests. Blur regions (only for selenium) within a page to ignore comparison (helpful when there are dynamic elements like text etc in a page). Support SeleniumLibrary(tested) , Selenium2Library(tested) and AppiumLibrary(not tested).
## Requirements
- Install the `robotframework-eyes` library using `pip`: 
```
    pip install robotframework-eyes
```     
- Install `Imagemagick` (for mac: `brew install imagemagick`, linux: `apt-get install imagemagick`) <br/>

-- **Important Imagemagick7: Make sure that you check the _Install Legacy Utilities (e.g. convert, compare)_ check mark in the installation process and that the directory to ImageMagick is in your PATH env variable. Please ensure that compare.exe is in your path env variable. If you still dont see diff images being generated, please downgrade to Imagemagick6** 

## Quick-reference Usage Guide
- Import the Library into your Robot test. E.g: <br/>    
 ```
    Library    RobotEyes
 ```    
- Call the `Open Eyes` keyword after opening the browser in your selenium test.
- Use the `Capture Full Screen` and `Capture Element` keywords to capture images.
- Call the `Compare Images` keyword at the end of the test to compare all the images captured in the respective test.
- Once done running the tests, report with name `visualReport.html` should be generated at the root of the project
- You can manually generate the report by running the below command. Eg:<br/>
```
    reportgen --baseline=<baseline image directory> --results=<output directory>
``` 
## Usage Guide
This guide contains the suggested steps to efficently integrate `RobotEyes` library into your Robot Framework test development workflow.<br/>
It also serves as documentation to clarify how this library functions on a high level.

## Keyword Documentation
| Keyword                | Arguments                        | Comments                                                                                    |
|------------------------|----------------------------------|---------------------------------------------------------------------------------------------|
| Open Eyes              | lib, tolerance, template_id, cleanup                   | Ex `open eyes  lib=AppiumLibrary  tolerance=5  cleanup=all_passed`                                                |
| Capture Full Screen    | tolerance, blur, radius, name, redact          | Ex `capture full screen  tolerance=5  name=homepage  blur=<array of locators>` radius=50(thickness of blur) |
| Capture Element        | locator, tolerance, blur, radius, name, redact |                                                                                             |
| Capture Mobile Element | locator, tolerance, blur, radius, name, redact |                                                                                             |
| Scroll To Element      | locator                          | Ex `scroll to element  id=user`                                                             |
| Compare Images         |                                  | Compares all the images captured in the test with their respective base image               |
| Compare Two Images     | first, second, output, tolerance | Compares two images captured in the above steps. Takes image names, diff file name and tolerance as arguments Ex: Compare Two Images  img1  img2  diff  10|

## Cleanup Options
This is only set when invoking open eyes
- all_passed
  - This will cleanup diff and actual folders that passed
- diffs_passed
  - Will only cleanup diffs that passed, leaving actuals in place
- actuals_passed
  - Will only cleanup actuals that passed, leaving diffs in place
- None
  - Won't do any image folder cleanups (default)

### Running Tests ###
`robot -d results -v images_dir:<baseline_images_directory> tests`<br/>
If baseline image directory does not exist, RobotEyes will create it.
If baseline image(s) does not exist, RobotEyes will move the captured image into the baseline directory.
For example, when running tests the first time all captured images will be moved to baseline directory passed by you (images_dir) <br/>
**Important** It is mandatory to pass baseline image directory, absence of which will throw an exception.<br/>

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
Library    SeleniumLibrary
Library    RobotEyes

*** Test Cases ***    
Sample visual regression test case  # Name of the example test case
    Open Browser    https://www.google.com/    chrome
    Maximize Browser Window
    Open Eyes    SeleniumLibrary(AppiumLibrary)  5
    Wait Until Element Is Visible    id=lst-ib
    Capture Full Screen
    Compare Images
    Close Browser
```
### Comparing the images
To compare the images, the following needs to exist in the TC's code:
- Library declaration:
```robotframework
Library    RobotEyes
```
- The `Open Eyes` keyword after the `Open Browser` keyword.
- Any of the image capture keywords. E.g `Capture Full Screen`
- The `Compare Images` keyword after capturing the desired images.

For Example:
```robotframework
*** Settings ***
Library    SeleniumLibrary
Library    RobotEyes

*** Test Cases ***    
Sample visual regression test case  # Name of the example test case
    Open Browser    https://www.google.com/    chrome
    Maximize Browser Window
    Open Eyes    SeleniumLibrary  5
    Wait Until Element Is Visible    id=lst-ib
    Capture Full Screen
    Compare Images
    Close Browser
```
After the comparison is completed (i.e. the `Compare Images` keyword in the TC is executed), a difference image will be generated and stored in the `diff` directory.<br/>
Also, a text file will be created containing the result of the comparison between the RMSE (root mean squared error) of the `diff` image and the tolerance set by the user.<br/>
After that, the regular Robot Framework report will raise a failure if the comparison fails.

### Another test example
```robotframework
*** Settings ***
Library    SeleniumLibrary
Library    RobotEyes

*** Variables ***
@{blur}    id=body    css=#SIvCob

*** Test Cases ***    
Sample visual regression test case  # Name of the example test case
    Open Browser    https://www.google.com/    chrome
    Maximize Browser Window
    Open Eyes    SeleniumLibrary  5
    Wait Until Element Is Visible    id=lst-ib
    # Below, the optional arguments are the tolerance to override global value, the regions to blur in the image and
    # the thickness of the blur (radius of Gaussian blur applied to the regions) 
    Capture Full Screen    10(tolerance)    ${blur}    50
    Capture Element    id=hplogo
    Compare Images
    Close Browser
```

### Non web/mobile image comparison tests
You can run plain non web/mobile image comparison tests as well. Here is an example:
```robotframework
*** Settings ***
Library    RobotEyes


*** Test Cases ***    
Plain image comparison test case  # Name of the example test case
    Open Eyes    lib=none  5
    Compare Two Images   ref=oldsearchpage.png   actual=newsearchpage.png   output=diffimage.png  tolerance=5
```
You need to place images to compare within two folders and provide their path while running the tests.<br/>
`robot -d results -v images_dir:<reference_directory> -v actual_dir:<actual_directory>  Tests/nonwebtest.robot`

**Important** Do not run non web tests and web/mobile tests together. This will result in errors during report creation.

### Template Tests
When writing a data driven Template Test, you need to provide a unique template_id in order to uniquely save images for each test.
```robotframework
*** Settings ***
Library  SeleniumLibrary
Library  RobotEyes

*** Test Cases ***
Sample test
    [Template]   Sample keyword
    https://www.google.com/   0
    https://www.google.com/   1
    https://www.google.com/   2


*** Keywords ***
Sample keyword
    [Arguments]  ${url}  ${uid}
    open browser  ${url}  chrome
    open eyes  SeleniumLibrary   template_id=${uid}
    sleep  3
    capture element  id=hplogo
    capture element  id=body  50
    compare images
    close browser
```

## Tolerance
Tolerance is the allowed dissimilarity between images. If comparison difference is more than tolerance, the test fails.<br/>
You can pass tolerance globally to the `open eyes` keyword. Ex `Open Eyes  lib=SeleniumLibrary  tolerance=5`.<br/>
Additionally you can override global tolerance by passing it to `Capture Element`, `Capture Fullscreen` keywords.<br/>
Ex: 
```Capture Element  <locator>  tolerance=10  blur=${locators}```<br/>
Tolerance should range between 1 to 100<br/>

## Blurring elements from image
You can also blur out unwanted elements (dynamic texts etc) from image to ignore them from comparison. This can help in getting more accurate test results. You can pass a list of locators or a single locator as argument to `Capture Element` and `Capture Full Screen` keywords.<br/>
Ex: ```Capture Element  <locator>  blur=id=test```
```
    @{blur}    id=body    css=#SIvCob
    Capture Element   <locator>  blur=${blur}
    Capture Full Screen     blur=${blur}
```
## Redacting elements from image
If blurring elements does not serve your purpose, you can redact elements from images. Simply pass a list of locators that you want to redact as argument to the capture keywords.
Ex: ```Capture Element  <locator>  redact=id=test```
```
    @{redact}    id=body    css=#SIvCob
    Capture Element   <locator>  redact=${redact}
    Capture Full Screen     redact=${redact}
```

## Basic Report
![Alt text](/basicreport.png "Basic Report")

Basic report should be autogenerated after execution (not supported for pabot). Alternatively, you can generate report by running the following command.</br>
```
    reportgen --baseline=<baseline image folder> --results=<results folder>
```

**Important: If you want to remotely view the report on Jenkins, you might need to update the CSP setting,
Refer:** https://wiki.jenkins.io/display/JENKINS/Configuring+Content+Security+Policy#ConfiguringContentSecurityPolicy-HTMLPublisherPlugin

## Interactive Report
Robot Eyes generates a report automatically after all tests have been executed. However a more interactive and intuitive flask based report is available.<br/>

You can view passed and failed tests and also use this feature to move acceptable actual images to baseline directory.
Run eyes server like this. `eyes --baseline=<baseline image directory> --results=<outputdir>(leave empty if output is at project root)`

![Alt text](/overview.png "Home screen")
![Alt text](/tests.png "Tests List")
![Alt text](/images.png "Images")

You can move selected images in a testcase by selecting images and clicking on "Baseline Images" button.</br>
You can also move all images of test cases by selecting the test cases you want to baseline and clicking on "Baseline Images" button.</br>

**Note: You need to have gevent library installed in the machine to be able to use eyes server.**</br>

## Pabot users
Visual tests can be executed in parallel using pabot to increase the speed of execution. Generate the report using `reportgen --baseline=<baseline images folder> --results=<results folder>` after running the tests.

## Contributors:
[Adirala Shiva](https://github.com/adiralashiva8) Contributed in creating a robotmetrics inspired reporting for RobotEyes.</br>
[DiegoSanchezE](https://github.com/DiegoSanchezE) Added major improvements in the ReadMe.</br>
[Priya](https://www.linkedin.com/in/priyamarimuthu) Contributes by testing and finding bugs/improvements before every release.</br>
[Ciaran Doheny](ciaran@flipdish.ie) Actively testing and suggesting improvements.

## Note
If you find this library useful, you can support me by doing the following:<br/> 
    - Star the repository.<br/>
    - Make a donation via [Paypal](https://paypal.me/jessezach). You can request for features and I will prioritise them for you.</br>

For any issue, feature request or clarification feel free to raise an issue in github or email me at iamjess988@gmail.com
