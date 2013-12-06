"""
Engine Core API

Provides a RESTful endpoint to the Engine

payload components:

app_name
sparql_endpoint or graph url or graph json

"""
import os
import re
import json
import hashlib
import subprocess
from uuid import uuid1

from flask import Flask
from flask import render_template, jsonify, make_response
from flask.ext.restful import reqparse, abort, Api, Resource

from werkzeug.contrib.fixers import ProxyFix

from utils import parse_payload, submit_job

app = Flask(__name__)

# wsgi interface for gunicorn
app.wsgi_app = ProxyFix(app.wsgi_app)

# use gunicorn port
app.config['PORT'] = int(os.environ.get('PORT', 8000))
app.config['DEBUG'] = bool(os.environ.get('DEBUG', True))

# keep track of submitted jobs and contexts
app.jobs = {}
app.context = {}

# wrap app with flask-restful
api = Api(app)

# configure request params
parser = reqparse.RequestParser()
parser.add_argument('payload', type=str)
parser.add_argument('job_id', type=str)
parser.add_argument('file_id', type=str)


def abort_if_job_doesnt_exist(job_id):
    if job_id not in api.app.jobs:
        abort(404, message="Job {} doesn't exist".format(job_id))


class Root(Resource):
    """Root level of provides a human readable description of the engine"""
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
    """JobList Resource"""
    def get(self):
        """Provides a list of all jobs being run on the engine"""
        return make_response(jsonify(api.app.jobs))

    def put(self):
        """Create a new job and add it to the queue."""
        args = parser.parse_args()
        context = json.loads(args['payload'])['@context']
        g = parse_payload(args['payload'])
        iri_sha1 = hashlib.sha1(str(g.identifier)).hexdigest()

        # create working directory
        wd = '/tmp/%s' % iri_sha1
        if not os.path.exists(wd):
            os.makedirs(wd)
        # save a copy of the submitted graph
        with open(os.path.join(wd, 'in_graph.jsonld'), 'w') as fopen:
            fopen.write(json.dumps(args['payload']))

        # submit the graph to be processed
        job_json_ld = submit_job(g, context)
        print job_json_ld
        with open(os.path.join(wd, 'response.jsonld'), 'w') as fopen:
            fopen.write(job_json_ld)

        # update the job graph
        api.app.jobs.update(json.loads(job_json_ld))

        # response should be a json-ld graph
        return make_response(jsonify(api.app.jobs))

api.add_resource(JobList, '/jobs')


class Job(Resource):
    """
    Job Resource

    Provides an interface to a single job being run on the engine
    """
    def get(self, job_id):
        """Return current status of job from queue."""
        abort_if_job_doesnt_exist(job_id)
        return make_response(jsonify(id=job_id,
                                     resposnse=api.app.jobs[job_id]))

    def delete(self, job_id):
        """Remove a job from the queue."""
        abort_if_job_doesnt_exist(job_id)
        os.removedirs(api.app.jobs[job_id])
        del api.app.jobs[job_id]
        return make_response((jsonify(), 200, None))

    def post(self):
        """Update or replace an existing job resource"""
        return make_response(jsonify(error="Not Implemented"),
                             501, None)

api.add_resource(Job, '/jobs/<string:job_id>')


class FilesList(Resource):
    def get(self):
        pass


class Files(Resource):
    """Files Resource"""
    def get(self, location):
        """Return file from location."""
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

api.add_resource(Files, '/files/<path:location>')


class ServicesList(Resource):
    """ServicesList Resource"""
    def get(self):
        pass


class Services(Resource):
    """Services Resource"""
    def get(self):
        pass


if __name__ == '__main__':
    app.run()