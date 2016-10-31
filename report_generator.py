import os
import sys
import xml.etree.ElementTree as ET


path = os.path.dirname(os.path.abspath(__file__))
index = path.rfind('/')
lib_folder = path[index + 1:]
report_folder = path[:index]

try:
    report_path = sys.argv[1:][0]
except IndexError:
    raise IndexError('Please provide the path to xml report')

if not os.path.exists(path + '/actual/'):
    raise ValueError('Results directory does not exist')

if not os.path.exists(path + '/baseline/'):
    raise ValueError('Baseline directory does not exist')

if not os.path.exists(path + '/diff/'):
    raise ValueError('Diff directory does not exist')

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
    <td>%s</td
    </tr>
    <tr>
    <td colspan="12" class="hiddenRow"><div class="accordian-body collapse" value="%s">
    <table class="table table-bordered table-hover">
    <thead>
    <tr>
    <th>Baseline</th>
    <th>Actual</th>
    <th>Diff</th>
    <th>Diff value</th>
    </tr>
    </thead>
    <tbody>''' % (folder_name, test_name, folder_name)

    for filename in os.listdir(path + '/actual/' + folder_name):
        if filename.endswith('.png'):
            actual_img_path = lib_folder + '/actual/' + folder_name + '/' + filename
            baseline_img_path = lib_folder + '/baseline/' + folder_name + '/' + filename
            diff_img_path = lib_folder + '/diff/' + folder_name + '/' + filename
            html += '''
            <tr>
            <td><img src="%s" height="200" width="350"></td>
            <td><img src="%s" height="200" width="350"></td>
            <td><img src="%s" height="200" width="350"></td>
            ''' % (baseline_img_path, actual_img_path, diff_img_path)

        elif filename.endswith('.txt'):
            infile = open(path + '/actual/' + folder_name + '/' + filename, 'r')
            first_line = infile.readline().strip()
            infile.close()
            os.remove(path + '/actual/' + folder_name + '/' + filename)
            html += '''
            <td>%s</td></tr>''' % first_line

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
</body>
</html>'''

print 'Creating report at %s/visualReport.html' % report_folder
output = open(report_folder + '/visualReport.html', 'w')
output.write(html)
output.close()
