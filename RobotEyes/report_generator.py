import os
import xml.etree.ElementTree as ET
from time import sleep


def generate_report(baseline_folder, report_path, img_path):
    sleep(1)
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

    tree = ET.parse(report_path)
    for t in tree.findall('.//test'):
        test_name = t.get('name')
        folder_name = test_name.replace(' ', '_')

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

        for filename in os.listdir(baseline_folder + '/' + folder_name):
            if filename.endswith('.png'):
                html += '''<tr>'''
                if os.path.exists(os.path.join(baseline_folder, folder_name, filename)):
                    base_img_path = os.path.join(baseline_folder, folder_name, filename)
                    html += '''<td><a href="%s" target="_blank"><img src="%s" height="200" width="350"></a></td>''' \
                            % (base_img_path, base_img_path)
                else:
                    html += '''<td></td>'''

                if os.path.exists(os.path.join(img_path, 'actual', folder_name, filename)):
                    baseline_img_path = os.path.join(img_path, 'actual', folder_name, filename)
                    html += '''<td><a href="%s" target="_blank"><img src="%s" height="200" width="350"></a></td>''' \
                            % (baseline_img_path, baseline_img_path)

                else:
                    html += '''<td></td>'''

                arr = filename.split('.')
                if os.path.exists(os.path.join(img_path, 'diff', folder_name, filename)):
                    diff_img_path = os.path.join(img_path, 'diff', folder_name, filename)
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
    <style>
      tr.accordion-toggle:hover {
        cursor:pointer;
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

    print("Creating visual report at %s/visualReport.html" % os.getcwd())
    output = open(os.getcwd() + '/visualReport.html', 'w')
    output.write(html)
    output.close()
