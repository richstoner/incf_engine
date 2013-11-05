from app import app

from flask import render_template, jsonify, make_response

from uuid import uuid1
import re
import subprocess

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

@app.route('/submit', methods=['POST'])
def submit_job():
    """Submit a job to the queue."""
    id = uuid1().hex
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

@app.route('/file/<location>')
def get_file(location):
    """Return current status of job from queue."""
    return 'location: %s ' % location

@app.route('/info')
def get_info():
    return jsonify(info='info')
