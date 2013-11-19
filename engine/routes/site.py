"""
Engine Core API

Provides a RESTful endpoint to the Engine

payload components:

app_name
sparql_endpoint or graph url or graph json

"""
import os
import re
import subprocess
from uuid import uuid1

from flask import render_template, jsonify, make_response
from flask.ext.restful import reqparse, abort, Api, Resource

from app import app
from utils import parse_payload


api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('payload', type=str)
parser.add_argument('job_id', type=str)



class Root(Resource):
    """
    Root level of provides a human readable description of the engine
    """
    def get(self):
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('home.html'), 200, headers)

api.add_resource(Root, '/')


class SendTextFile(Resource):
    """Send your static text file."""
    def get(self, file_name):
        file_dot_text = file_name + '.txt'
        return api.app.send_static_file(file_dot_text)

api.add_resource(SendTextFile,  '/<file_name>.txt')


class JobList(Resource):
    """
    JobList Resource
    """
    def get(self):
        """Provides a list of all jobs being run on the engine"""
        return make_response(jsonify(api.app.jobs))

api.add_resource(JobList, '/jobs')


class Job(Resource):
    """
    Job Resource

    Provides an interface to a single job being run on the engine
    """
    def get(self, job_id):
        """Return current status of job from queue."""
        args = parser.parse_args()
        if args['job_id']:
            id = args['job_id']

            proc = subprocess.Popen('qstat -j %d' % app.jobs[id],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    shell=True)
            o, e = proc.communicate()
            return make_response(jsonify(status=o))
        else:
            return make_response(jsonify(api.app.jobs))

    def put(self):
        """Create a new job and add it to the queue."""
        args = parser.parse_args()
        in_graph = parse_payload(args['payload'])
        id = in_graph.identifier.n3()  # should be included in payload
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
        # response should be a json-ld grapb
        return make_response((jsonify(id=id, job_id=taskid), 201, None))

    def delete(self, job_id):
        """Remove a job from the queue."""
        try:
            proc = subprocess.Popen('qdel %d' % app.jobs[id],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    shell=True)
            o, _ = proc.communicate()
            del app.jobs[id]
            return make_response((o, 204, None))
        except Exception, e:
            return make_response(
                (jsonify(message='Could not remove job[%s] because %s'
                                 % (id, e)), 200, None))

    def post(self):
        """Update or replace an existing job resource"""

api.add_resource(Job, '/jobs/<string:job_id>')


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
