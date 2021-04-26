import os
import xml.etree.ElementTree as ET
from time import sleep

from .constants import IMAGE_EXTENSIONS

def generate_report(baseline_folder, results_folder, actual_folder=None):
    sleep(1)
    img_path = os.path.join(results_folder, 'visual_images')
    report_path = os.path.join(results_folder, 'output.xml')
    relative_baseline_folder_path = relative_path(baseline_folder, results_folder.replace(os.getcwd(), ''))
    relative_actual_folder_path = relative_path(actual_folder, results_folder.replace(os.getcwd(), '')) if actual_folder else ''

    html = '''
    <html>
    <head>
        <meta content="text/html;charset=utf-8" http-equiv="Content-Type">
        <meta content="utf-8" http-equiv="encoding">
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css" integrity="sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO" crossorigin="anonymous">
        <link rel="stylesheet" href="http://fonts.googleapis.com/css?family=Roboto:300,400,500,700" type="text/css">
        <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.3.1/css/all.css" integrity="sha384-mzrmE5qonljUremFsqc01SB46JvROS7bZs3IO2EmfFsd15uHvIt+Y8vEf7N7fWAU" crossorigin="anonymous">
        <script src="https://code.jquery.com/jquery-3.3.1.slim.min.js" integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo" crossorigin="anonymous"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.3/umd/popper.min.js" integrity="sha384-ZMP7rVo3mIykV+2+9J3UJ46jBk0WLaUAdn689aCwoqbBJiSnjAK/l8WvCWPIPm49" crossorigin="anonymous"></script>
        <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/js/bootstrap.min.js" integrity="sha384-ChfqqxuZUCnJSK3+MXmPNIyE6ZbWh2IMqE241rYiqJxyMiZ6OW/JmZQ5stwEULTy" crossorigin="anonymous"></script>
        <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
        <script src="https://code.highcharts.com/highcharts.js"></script>
        <script src="http://code.highcharts.com/highcharts-3d.js"></script>
    </head>
    <body>
    <div id="piechart"></div>
    <div class="container" style="position:relative;top:20px;">
    <table class="table table-striped table-sm" id="results">
    <thead>
    <tr>
    <th></th>
    <th>Test Name</th>
    </tr>
    </thead>
    <tbody>
    '''

    try:
        tree = ET.parse(report_path)
    except FileNotFoundError:
        return

    for t in tree.findall('.//test'):
        if not t.findall('.//kw[@name="Open Eyes"]'):
            continue

        test_name = t.get('name')
        folder_name = test_name.replace(' ', '_')

        # If the test folder does not exist, we know that it's probably a data driven test. Unless there was some other exception.
        if not os.path.exists(os.path.join(img_path, 'actual', folder_name)):
            for open_eyes_keyword in t.findall('.//kw[@name="Open Eyes"]'):
                # Get the actual test folder name from the message we log within open eyes keyword
                folder_name = get_template_test_name(open_eyes_keyword)

                if folder_name:
                    if actual_folder:
                        html = make_non_web_test_table(html, baseline_folder, relative_baseline_folder_path, img_path,
                                                       test_name, folder_name, actual_folder,
                                                       relative_actual_folder_path)
                    else:
                        html = make_test_table(html, baseline_folder, relative_baseline_folder_path, img_path, test_name,
                                        folder_name)
        else:
            if actual_folder:
                html = make_non_web_test_table(html, baseline_folder, relative_baseline_folder_path, img_path,
                                               test_name, folder_name, actual_folder, relative_actual_folder_path)
            else:
                html = make_test_table(html, baseline_folder, relative_baseline_folder_path, img_path, test_name,
                                       folder_name)
    html += '''
    </tbody>
    </table>
    </div>
    <style>
      tr.accordion-toggle:hover {
        cursor:pointer;
      }
      img {
        image-rendering: pixelated;
        object-fit: contain;
      }
    </style>
    <script>
        $(document).ready(function() {
          var pass = 0;
          var fail = 0;
          var t = 1;
          $("table#innerResults").each(function() {
            var $items = $(this).find('tbody tr');
            $.each($items, function(n, e) {
              color = $(e).find('td:last').css('color');
              if (color == 'rgb(255, 0, 0)') {
                return false;
              }
            });
            if(color == 'rgb(255, 0, 0)') {
              $('table#results > tbody > tr:nth-child(' + t + ') > td:nth-child(2)').css('color','red');
              t = t+2;
              fail = fail + 1;
            }
            else  {
             $('table#results > tbody > tr:nth-child(' + t + ') > td:nth-child(2)').css('color','green');
             t = t+2;
             pass = pass + 1;
            }
          });

          $("tr.accordion-toggle").click(function () {
            classes = {
                "fa-arrow-down": "fa-arrow-right",
                "fa-arrow-right": "fa-arrow-down"
            }
            cls = $(this).find('i:first').attr("class").split(" ")[1];
            $(this).find('i:first').removeClass(cls).addClass(classes[cls]);
          });

          Highcharts.chart('piechart', {
            chart: {
                type: 'pie',
                options3d: {
                    enabled: true,
                    alpha: 45,
                    beta: 0
                }
            },
            title: {
                text: 'Test result stats'
            },
            tooltip: {
                pointFormat: '{series.name}: <b>{point.y:.1f}</b>'
            },
            plotOptions: {
                pie: {
                    allowPointSelect: true,
                    cursor: 'pointer',
                    depth: 35,
                    colors: ['#32CD32', '#B22222'],
                    dataLabels: {
                        enabled: true,
                        format: '<b>{point.name}</b>: {point.y:.1f}',
                        style: {
                            color: (Highcharts.theme && Highcharts.theme.contrastTextColor) || 'black'
                        }
                    }
                }
            },
            series: [{
                name: 'Count',
                colorByPoint: true,
                data: [{
                    name: 'Pass',
                    y: pass,
                    sliced: true,
                    selected: true
                }, {
                    name: 'Fail',
                    y: fail
                }]
            }]
          });
        });
    </script>
    </body>
    </html>'''

    output_path = os.path.join(os.getcwd(), results_folder, 'visualReport.html')
    print("Creating visual report at %s" % output_path)
    output = open(output_path, 'w')
    output.write(html)
    output.close()

def get_template_test_name(open_eyes_keyword):
    for element in open_eyes_keyword.findall('.//msg'):
        if element.text.startswith("roboteyestestfolder"):
            return element.text.split(":")[1].strip()
    return ""

def relative_path(baseline_folder, results_folder):
    if baseline_folder.startswith(os.path.sep):
        baseline_folder = baseline_folder[1:]
    # This condition to avoid fixing absolute paths
    if os.path.exists(os.getcwd() + os.path.sep + baseline_folder) and not os.path.isabs(baseline_folder):
        results_folder = results_folder[1:] if results_folder.startswith(os.path.sep) else results_folder
        count = get_count_of_sub_directories(results_folder)
        s = ''
        for i in range(count):
            s = s + ('..' + os.path.sep)
        s += baseline_folder
        return s
    else:
        # Does not exist within project root or absolute path
        return os.path.sep + baseline_folder


def get_count_of_sub_directories(results_path):
    count = 0
    if not results_path.startswith(os.path.sep):
        results_path = os.path.sep + results_path

    for i in range(1, len(results_path)):
        if results_path[i] != os.path.sep and results_path[i-1] == os.path.sep:
            count += 1
    return count


def make_test_table(html, baseline_folder, relative_baseline_folder_path, img_path, test_name, folder_name):
    html += '''<tr data-toggle="collapse" data-target='div[value="%s"]' class="accordion-toggle">
            <td>
            <button class="btn btn-default btn-sm"><i class="fas fa-arrow-right"></i></button>
            </td>
            <td>%s</td>
            </tr>
            <tr>
            <td colspan="12" class="hiddenRow"><div class="accordian-body collapse" value="%s">
            <table class="table table-bordered table-hover" id="innerResults">
            <thead>
            <tr>
            <th style="text-align:center;vertical-align:middle">Baseline</th>
            <th style="text-align:center;vertical-align:middle">Actual</th>
            <th style="text-align:center;vertical-align:middle">Diff</th>
            <th>Diff value<br><font size="2">(Exp : Actual)</font></th>
            </tr>
            </thead>
            <tbody>''' % (folder_name, test_name, folder_name)

    for filename in os.listdir(baseline_folder + os.path.sep + folder_name):
        if filename.endswith('.png'):
            html += '''<tr>'''
            if os.path.exists(os.path.join(baseline_folder, folder_name, filename)):
                base_img_path = os.path.join(relative_baseline_folder_path, folder_name, filename)
                html += '''<td><a href="%s" target="_blank"><img src="%s" height="200" width="350"></a></td>''' \
                        % (base_img_path, base_img_path)
            else:
                html += '''<td></td>'''

            if os.path.exists(os.path.join(img_path, 'actual', folder_name, filename)):
                actual_img_path = os.path.join('visual_images', 'actual', folder_name, filename)
                html += '''<td><a href="%s" target="_blank"><img src="%s" height="200" width="350"></a></td>''' \
                        % (actual_img_path, actual_img_path)
            else:
                html += '''<td></td>'''

            arr = filename.split('.')
            if os.path.exists(os.path.join(img_path, 'diff', folder_name, filename)):
                diff_img_path = os.path.join('visual_images', 'diff', folder_name, filename)
                html += '''<td><a href="%s" target="_blank"><img src="%s" height="200" width="350"></a></td>''' \
                        % (diff_img_path, diff_img_path)
            elif os.path.exists(
                    img_path + os.path.sep + 'diff' + os.path.sep + folder_name + os.path.sep + arr[0] + '-0.png'):
                diff_img_path = 'visual_images' + os.path.sep + 'diff' + os.path.sep + \
                                folder_name + os.path.sep + arr[0] + '-0.png'
                html += '''<td><a href="%s" target="_blank"><img src="%s" height="200" width="350"></a></td>''' \
                        % (diff_img_path, diff_img_path)
            else:
                html += '''<td></td>'''
            txt_file = img_path + os.path.sep + 'actual' + os.path.sep + \
                       folder_name + os.path.sep + filename + ".txt"
            if os.path.exists(txt_file):
                infile = open(img_path + os.path.sep + 'actual' + os.path.sep + folder_name +
                              os.path.sep + filename + ".txt", 'r')
                first_line = infile.readline().strip()
                arr = first_line.split()
                infile.close()
                html += '''
                        <td style="color:%s;">%s</td></tr>''' % (arr[1].lower(), arr[0])
            else:
                html += '''<td></td></tr>'''

    html += '''
            </tbody>
            </table>
            </div>
            </td>
            </tr>'''
    return html


def make_non_web_test_table(html, baseline_folder, relative_baseline_folder_path, img_path, test_name,
                            folder_name, actual_folder, relative_actual_folder_path):
    html += '''<tr data-toggle="collapse" data-target='div[value="%s"]' class="accordion-toggle">
                <td>
                <button class="btn btn-default btn-sm"><i class="fas fa-arrow-right"></i></button>
                </td>
                <td>%s</td>
                </tr>
                <tr>
                <td colspan="12" class="hiddenRow"><div class="accordian-body collapse" value="%s">
                <table class="table table-bordered table-hover" id="innerResults">
                <thead>
                <tr>
                <th style="text-align:center;vertical-align:middle">Baseline</th>
                <th style="text-align:center;vertical-align:middle">Actual</th>
                <th style="text-align:center;vertical-align:middle">Diff</th>
                <th>Diff value<br><font size="2">(Exp : Actual)</font></th>
                </tr>
                </thead>
                <tbody>''' % (folder_name, test_name, folder_name)

    test_folder = os.path.join(img_path, 'actual', folder_name)

    for filename in os.listdir(test_folder):
        if filename.split('.')[-1] in IMAGE_EXTENSIONS:
            file = open(test_folder + os.path.sep + filename + '.txt', 'r')
            content = file.read()
            result, names = content.split('\n')
            file.close()

            names_arr = names.split()
            baseline_img_path = os.path.join(baseline_folder, names_arr[0])
            actual_img_path = os.path.join(actual_folder, names_arr[1])
            html += '''<tr>'''
            if os.path.exists(baseline_img_path):
                base_img_path = os.path.join(relative_baseline_folder_path, names_arr[0])
                html += '''<td><a href="%s" target="_blank"><img src="%s" height="200" width="350"></a></td>''' \
                        % (base_img_path, base_img_path)
            else:
                html += '''<td></td>'''

            if os.path.exists(actual_img_path):
                actual_img_path = os.path.join(relative_actual_folder_path, names_arr[1])
                html += '''<td><a href="%s" target="_blank"><img src="%s" height="200" width="350"></a></td>''' \
                        % (actual_img_path, actual_img_path)
            else:
                html += '''<td></td>'''

            arr = filename.split('.')
            if os.path.exists(os.path.join(img_path, 'actual', folder_name, filename)):
                diff_img_path = os.path.join('visual_images', 'actual', folder_name, filename)
                html += '''<td><a href="%s" target="_blank"><img src="%s" height="200" width="350"></a></td>''' \
                        % (diff_img_path, diff_img_path)
            elif os.path.exists(
                    img_path + os.path.sep + 'actual' + os.path.sep + folder_name + os.path.sep + arr[0] + '-0.png'):
                diff_img_path = os.path.join('visual_images', 'actual', folder_name) + os.path.sep + arr[0] + '-0.png'
                html += '''<td><a href="%s" target="_blank"><img src="%s" height="200" width="350"></a></td>''' \
                        % (diff_img_path, diff_img_path)
            else:
                html += '''<td></td>'''

            if result:
                arr = result.split()
                html += '''
                            <td style="color:%s;">%s</td></tr>''' % (arr[1].lower(), arr[0])
            else:
                html += '''<td></td></tr>'''

    html += '''
                </tbody>
                </table>
                </div>
                </td>
                </tr>'''
    return html