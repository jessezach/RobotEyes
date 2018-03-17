import os
import sys
import xml.etree.ElementTree as ET


def generate_report(root_folder, report_path, img_path):
    html = '''
    <html>
    <head>
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css"
              integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">
        <link rel="stylesheet" href="http://fonts.googleapis.com/css?family=Roboto:300,400,500,700" type="text/css">
        <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.12.2/jquery.min.js"></script>
        <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"
                integrity="sha384-Tc5IQib027qvyjSMfHjOMaLkfuWVxZxUPnCJA7l2mCWNIpG9mGCD8wGNIcPD7Txa"
                crossorigin="anonymous"></script>
    </head>
    <body>
    <h4 class="text-center">Visual test report</h4>
    <div class="container" style="position:relative;top:20px;">
    <table class="table table-striped table-hover" id="results">
    <thead>
    <tr>
    <th></th>
    <th>Test Name</th>
    </tr>
    </thead>
    <tbody>
    '''

    tree = ET.parse(report_path)
    for t in tree.findall('.//test'):
        test_name = t.get('name')
        folder_name = test_name.replace(' ', '_')

        html += '''<tr data-toggle="collapse" data-target='div[value="%s"]' class="accordion-toggle">
        <td>
        <button class="btn btn-default btn-sm"><span class="glyphicon glyphicon-plus"></span></button>
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

        for filename in os.listdir(img_path + '/baseline/' + folder_name):
            if filename.endswith('.png'):
                html += '''<tr>'''
                if os.path.exists(img_path + '/baseline/' + folder_name + '/' + filename):
                    actual_img_path = img_path + '/baseline/' + folder_name + '/' + filename
                    html += '''<td><a href="%s" target="_blank"><img src="%s" height="200" width="350"></a></td>''' \
                            % (actual_img_path, actual_img_path)
                else:
                    html += '''<td></td>'''

                if os.path.exists(img_path + '/actual/' + folder_name + '/' + filename):
                    baseline_img_path = img_path + '/actual/' + folder_name + '/' + filename
                    html += '''<td><a href="%s" target="_blank"><img src="%s" height="200" width="350"></a></td>''' \
                            % (baseline_img_path, baseline_img_path)

                else:
                    html += '''<td></td>'''

                arr = filename.split('.')
                if os.path.exists(img_path + '/diff/' + folder_name + '/' + filename):
                    diff_img_path = img_path + '/diff/' + folder_name + '/' + filename
                    html += '''<td><a href="%s" target="_blank"><img src="%s" height="200" width="350"></a></td>'''\
                            % (diff_img_path, diff_img_path)
                
                elif os.path.exists(img_path + '/diff/' + folder_name + '/' + arr[0] + '-0.png'):
                    diff_img_path = img_path + '/diff/' + folder_name + '/' + arr[0] + '-0.png'
                    html += '''<td><a href="%s" target="_blank"><img src="%s" height="200" width="350"></a></td>'''\
                            % (diff_img_path, diff_img_path)

                else:
                    html += '''<td></td>'''

                txt_file = img_path + '/actual/' + folder_name + '/' + filename + ".txt"
                if os.path.exists(txt_file):
                    infile = open(img_path + '/actual/' + folder_name + '/' + filename + ".txt", 'r')
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

    html += '''
    </tbody>
    </table>
    </div>
    <script>
        $(document).ready(function() {
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
            }
            else  {
             $('table#results > tbody > tr:nth-child(' + t + ') > td:nth-child(2)').css('color','green');
             t = t+2;
            }
          });
        });
    </script>
    </body>
    </html>'''

    print("Creating visual report at %s/visualReport.html" % root_folder)
    output = open(root_folder + '/visualReport.html', 'w')
    output.write(html)
    output.close()


if __name__ == "__main__":
    root_folder = os.getcwd()
    import os

    try:
        output_dir = sys.argv[1]

    except IndexError:
        print("Assuming results stored in root..")
        output_dir = ""

    if output_dir.endswith('/') or not output_dir:
        report_path = output_dir + 'output.xml'
        img_path = output_dir + 'visual_images'

    else:
        report_path = output_dir + '/output.xml'
        img_path = output_dir + '/visual_images'

    if os.path.exists(root_folder + "/" + report_path) and os.path.exists(root_folder + "/" + img_path):
        generate_report(root_folder, report_path, img_path)
    else:
        raise Exception("Please provide a valid path to results.")
