"""
Engine Core API

Provides a RESTful endpoint
"""
import os
import re
import subprocess
from uuid import uuid1

from flask import render_template, jsonify, make_response

from app import app

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')


@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html')


@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)

"""
payload components:

app_name
sparql_endpoint or graph url or graph json
"""
@app.route('/submit', methods=['POST'])
def submit_job():
    """Submit a job to the queue."""
    id = uuid1().hex
    wd = '/data/%s' % id
    if not os.path.exists(wd):
        os.makedirs(wd)
    proc = subprocess.Popen('qsub -b yes sleep 60', stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, shell=True)
    o, e = proc.communicate()
    lines = [line for line in o.split('\n') if line]
    taskid = int(re.match("Your job ([0-9]*) .* has been submitted",
                          lines[-1]).groups()[0])
    app.jobs[id] = taskid
    print app.jobs
    return make_response((jsonify(id=id, job_id=taskid), 201, None))

@app.route('/destroy/<id>')
def destroy_job(id):
    """Remove a job from the queue."""
    try:
        proc = subprocess.Popen('qdel %d' % app.jobs[id], stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, shell=True)
        o, _ = proc.communicate()
        del app.jobs[id]
        return make_response((o, 204, None))
    except Exception, e:
        return make_response((jsonify(message=('Could not remove job[%s] '
                                               'because %s') % (id, e)),
                              200, None))

@app.route('/status/<id>')
def job_status(id):
    """Return current status of job from queue."""
    proc = subprocess.Popen('qstat -j %d' % app.jobs[id], stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, shell=True)
    o, e = proc.communicate()
    return jsonify(status=o)

@app.route('/file/<path:location>')
def get_file(location):
    """Return current status of job from queue."""
    response = make_response()
    response.headers['Content-Description'] = 'File Transfer'
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['Content-Type'] = 'application/octet-stream'
    if not '/' in location:
        file_basename = location
        path = '/adhd200/'
        file_size = os.stat(os.path.join(path, location)).st_size
        response.headers['Content-Disposition'] = 'attachment; filename=%s' % file_basename
        response.headers['Content-Length'] = file_size
        response.headers['X-Accel-Redirect'] = os.path.join(path, location) # nginx: http://wiki.nginx.org/NginxXSendfile
        return response
    location = '/' + location
    print location
    file_basename = os.path.split(location)[-1]
    file_size = os.stat(location).st_size
    response.headers['Content-Disposition'] = 'attachment; filename=%s' % file_basename
    response.headers['Content-Length'] = file_size
    response.headers['X-Accel-Redirect'] = location # nginx: http://wiki.nginx.org/NginxXSendfile
    return response

@app.route('/info')
def get_info():
    return jsonify(info='info',
                   query='',
                   )
