from flask import Flask, render_template, flash, redirect
from gevent import pywsgi
import shutil
import os

app = Flask(__name__, static_url_path="", static_folder=os.getcwd(), template_folder='templates')

app.debug = True

app.secret_key = 'jevjebvjbdf'

@app.route("/")
def report():
    baseline_path = os.path.join(results, 'visual_images', 'baseline')
    actual_path = os.path.join(results, 'visual_images', 'actual')
    diff_path = os.path.join(results, 'visual_images', 'diff')

    data = {}
    if os.path.exists(actual_path):
        for directory in os.listdir(os.path.join(actual_path)):
            abs_directory = os.path.join(actual_path, directory)

            if os.path.isdir(abs_directory):
                test_name = directory.replace('_', ' ')

                data[test_name] = []

                for file in os.listdir(abs_directory):
                    if file.endswith('.png'):
                        row = []

                        b_img = os.path.join(baseline_path, directory, file)

                        row.append(b_img)
                        row.append(os.path.join(abs_directory, file))
                        row.append(os.path.join(diff_path, directory, file))

                        txt_file_name = file + '.txt'
                        txt_file_path = os.path.join(abs_directory, txt_file_name)

                        if os.path.exists(txt_file_path):
                            obj = open(txt_file_path, 'r')
                            first_line = obj.readline().strip()
                            arr = first_line.split()
                            obj.close()
                            row.append(arr)

                        row.append(directory)
                        data[test_name].append(row)
    return render_template('report.html', data=data)


@app.route("/baseline", methods=['POST'])
def make_all_baseline():
    baseline_path = os.path.join(results, 'visual_images', 'baseline')
    actual_path = os.path.join(results, 'visual_images', 'actual')

    for directory in os.listdir(os.path.join(actual_path)):

        if os.path.isdir(os.path.join(actual_path, directory)):
            abs_directory = os.path.join(actual_path, directory)
            b_directory = os.path.join(baseline_path, directory)

            if os.path.exists(b_directory):
                shutil.rmtree(b_directory)

            shutil.copytree(abs_directory, b_directory)

    flash('Successfully moved all images.')
    return redirect('/')


@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 0 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r


def start(res, host, port):
    global results
    results = res
    app.logger.info('Starting server on %s:%s' % (host, port))

    try:
        pywsgi.WSGIServer((host, int(port)),
                      app).serve_forever()
    except KeyboardInterrupt:
        print('Exiting...')
