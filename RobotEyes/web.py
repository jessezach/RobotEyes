from flask import Flask, render_template, flash, redirect, url_for, request, jsonify
from gevent import pywsgi
import shutil
import os

app = Flask(__name__, static_url_path="", static_folder=os.getcwd(), template_folder='templates')

app.debug = True

app.secret_key = 'somerandomkey'


@app.route("/")
def overview():
    actual_path = os.path.join(results, 'visual_images', 'actual')
    passed = 0
    failed = 0

    if os.path.exists(actual_path):
        for directory in os.listdir(os.path.join(actual_path)):
            abs_directory = os.path.join(actual_path, directory)

            if os.path.isdir(abs_directory):
                last_found = ''  # incase we are inside an empty directory
                for file in os.listdir(abs_directory):
                    if file.endswith('.txt'):
                        f = os.path.join(abs_directory, file)
                        obj = open(f, 'r')
                        first_line = obj.readline().strip()
                        arr = first_line.split()
                        obj.close()
                        color = arr[1]

                        if color == 'red':
                            failed += 1
                            break

                        elif color == 'green':
                            last_found = 'green'
                else:
                    if last_found == 'green':
                        passed += 1

    return render_template('overview.html', passed=passed, failed=failed, total=(passed+failed))


@app.route("/passed")
def passed():
    data = {}

    actual_path = os.path.join(results, 'visual_images', 'actual')

    if os.path.exists(actual_path):
        for directory in os.listdir(os.path.join(actual_path)):
            test_name = directory.replace('_', ' ')

            abs_directory = os.path.join(actual_path, directory)

            if os.path.isdir(abs_directory):
                for file in os.listdir(abs_directory):
                    if file.endswith('.txt'):
                        f = os.path.join(abs_directory, file)

                        obj = open(f, 'r')
                        first_line = obj.readline().strip()
                        arr = first_line.split()
                        obj.close()
                        color = arr[1]

                        if color == 'red':
                            break
                else:
                    data[test_name] = directory

    return render_template('passed.html', passed=data)


@app.route("/failed")
def failed():
    data = []

    actual_path = os.path.join(results, 'visual_images', 'actual')

    if os.path.exists(actual_path):
        for directory in os.listdir(os.path.join(actual_path)):
            test_name = directory.replace('_', ' ')

            abs_directory = os.path.join(actual_path, directory)

            if os.path.isdir(abs_directory):

                for file in os.listdir(abs_directory):

                    if file.endswith('.txt'):
                        f = os.path.join(abs_directory, file)

                        obj = open(f, 'r')
                        first_line = obj.readline().strip()
                        arr = first_line.split()
                        obj.close()
                        color = arr[1]

                        if color == 'red':
                            data.append([test_name, directory])
                            break

    return render_template('failed.html', failed=data)

@app.route('/<test>')
def images(test):
    test_name = test.replace('_', ' ')
    output = {test_name: []}

    baseline_directory = os.path.join(baseline, test)
    actual_directory = os.path.join(results, 'visual_images', 'actual', test)
    diff_directory = os.path.join(results, 'visual_images', 'diff', test)

    if os.path.isdir(actual_directory):
        for file in os.listdir(actual_directory):
            if file.endswith('.png'):
                images = []
                images.append(os.path.join(baseline_directory, file))
                images.append(os.path.join(actual_directory, file))
                images.append(os.path.join(diff_directory, file))

                file = file + '.txt'
                f = os.path.join(actual_directory, file)

                if os.path.exists(f):
                    obj = open(f, 'r')
                    first_line = obj.readline().strip()
                    arr = first_line.split()
                    obj.close()
                    color = arr[1]
                    value = arr[0]
                    images.append(color)
                    images.append(value)
                    output[test_name].append(images)
    return render_template('test.html', data=output)

@app.route("/all")
def report():
    baseline_path = baseline
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


@app.route("/baseline_test", methods=['POST'])
def make_all_baseline():
    tests = request.json['tests']

    baseline_path = baseline
    actual_path = os.path.join(results, 'visual_images', 'actual')

    for test in tests:
        baseline_test = os.path.join(baseline_path, test)
        actual_test = os.path.join(actual_path, test)

        if os.path.exists(baseline_test):
            shutil.rmtree(baseline_test)

        shutil.copytree(actual_test, baseline_test)

    resp = {"success": True}
    return jsonify(resp)


@app.route("/baseline_images", methods=['POST'])
def baseline_images():
    imges = request.json['images']

    for img in imges:
        actual_path = os.path.join(results, img)
        baseline_path = actual_path.replace('/actual/', '/baseline/')

        if os.path.exists(actual_path):
            if os.path.exists(baseline_path):
                os.remove(baseline_path)
            shutil.copyfile(actual_path, baseline_path)

    resp = {'success': True}
    return jsonify(resp)


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


def start(base, res, host, port):
    global results
    global baseline
    results = res
    baseline = base
    app.logger.info('Starting server on %s:%s' % (host, port))

    try:
        pywsgi.WSGIServer((host, int(port)),
                      app).serve_forever()
    except KeyboardInterrupt:
        print('Exiting...')
