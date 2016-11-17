import os
import sys
import xml.etree.ElementTree as ET

path = os.path.dirname(os.path.abspath(__file__))
index = path.rfind('/')
root_folder = path[:index]

try:
    report_path = sys.argv[1]
    img_path = sys.argv[2]
except IndexError:
    raise IndexError('Please provide the path to xml report and images')

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
    <th>Baseline</th>
    <th>Actual</th>
    <th>Diff</th>
    <th>Diff value</th>
    </tr>
    </thead>
    <tbody>''' % (folder_name, test_name, folder_name)

    for filename in os.listdir(img_path + '/baseline/' + folder_name):
        if filename.endswith('.png'):
            html += '''<tr>'''
            if os.path.exists(img_path + '/baseline/' + folder_name + '/' + filename):
                actual_img_path = img_path + '/baseline/' + folder_name + '/' + filename
                html += '''<td><a href="%s" target="_blank"><img src="%s" height="200" width="350"></a></td>''' % (actual_img_path, actual_img_path)
            else:
                html += '''<td></td>'''

            if os.path.exists(img_path + '/actual/' + folder_name + '/' + filename):
                baseline_img_path = img_path + '/actual/' + folder_name + '/' + filename
                html += '''<td><a href="%s" target="_blank"><img src="%s" height="200" width="350"></a></td>''' % (baseline_img_path, baseline_img_path)
            else:
                html += '''<td></td>'''

            if os.path.exists(img_path + '/diff/' + folder_name + '/' + filename):
                diff_img_path = img_path + '/diff/' + folder_name + '/' + filename
                html += '''<td><a href="%s" target="_blank"><img src="%s" height="200" width="350"></a></td>''' % (diff_img_path, diff_img_path)
            else:
                html += '''<td></td>'''

            txt_file = img_path + '/actual/' + folder_name + '/' + filename + ".txt"
            if os.path.exists(txt_file):
                infile = open(img_path + '/actual/' + folder_name + '/' + filename + ".txt", 'r')
                first_line = infile.readline().strip()
                infile.close()
                os.remove(txt_file)
                html += '''
                <td>%s</td></tr>''' % first_line
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
        var max = 0.0;
        var $items = $(this).find('tbody tr');
        var len = $items.length;
        $.each($items, function(n, e) {
          diff = $(e).find('td:last').text()
          diff = parseFloat(diff);
          if (diff > max) {
            max = diff
          }
        });
        if(max < 0.1) {
          $('table#results > tbody > tr:nth-child(' + t + ') > td:nth-child(2)').css('color','green');
          t = t+2;
        }
        else if(max >= 0.1 && max < 0.2) {
          $('table#results > tbody > tr:nth-child(' + t + ') > td:nth-child(2)').css('color','orange');
          t = t+2;
        }
        else  {
         $('table#results > tbody > tr:nth-child(' + t + ') > td:nth-child(2)').css('color','red');
         t = t+2;
        }
      });
    });
</script>
</body>
</html>'''

print "Creating visual report at %s/visualReport.html" % root_folder
output = open(root_folder + '/visualReport.html', 'w')
output.write(html)
output.close()
