
__author__ = 'stonerri'

'''

This code acts as the application's primary controller, and provides links to the following:

'''




import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
import tornado.gen
import tornado.auth
import tornado.autoreload
from tornado.options import define, options
import oauth2

from redis import Redis
from rq import Queue

import requests
import sys, pprint, time, ConfigParser, os
from ConfigParser import SafeConfigParser

import json
import os.path
import uuid
import datetime
import logging
import random
import time
import string
from time import mktime, sleep

import github


define("port", default=8000, help="run on the given port", type=int)


root = os.path.dirname(__file__)

# needed to serialize any non-standard objects
class GenericEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return int(mktime(obj.timetuple()))

        return json.JSONEncoder.default(self, obj)

class FaviconHandler(tornado.web.RequestHandler):
    def get(self):
        self.redirect('/static/favicon.ico')

# generic object
class Object(object):
    pass


class BaseHandler(tornado.web.RequestHandler):

    @tornado.web.removeslash
    def get_current_user(self):
         return self.get_secure_cookie("user")

class LogoutHandler(BaseHandler):

    def get(self):

        self.clear_cookie("user")

        self.redirect(self.get_argument("next","/"))





class WebHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):

        print self.get_current_user()

        try:
            with open(os.path.join(root, 'templates/index.html')) as f:
                self.write(f.read())
        except IOError as e:
            self.write("404: Not Found")



from enginetasks import *

# websockets
class WSHandler(tornado.websocket.WebSocketHandler):

    def allow_draft76(self):
        # for iOS 5.0 Safari
        return True

    def open(self):
        print 'Websocket connection opened.'

        # self.write_message("Hello World")

    def on_close(self):
        print 'connection closed'

    def on_message(self, message):

        print 'message received %s' % message
        messagedict = json.loads(message)

        return_data = {}
        return_data['result'] = False
        return_data['callback_id'] = messagedict['callback_id']

        if messagedict['type'] == 'kickoff_queue':

            pass

            #job = self.application.q.enqueue(count_words_at_url, 'http://nvie.com')
            ##self.shared.js.append(job)
            #while not job.result:
            #    time.sleep(1)
            #
            #return_data['data'] = job.result
            #return_data['result'] = True
            #
            #print 'job complete'
            #print job.result
            #
            #self.write_message(json.dumps(return_data))



        #elif messagedict['type'] == 'dropbox':
        #
        #    job = self.application.q.enqueue(processDropboxImage, messagedict['files'])
        #    self.application.jobs.append(job)

        #elif messagedict['type'] == 't1':
        #
        #    job = self.application.q.enqueue(processT1, messagedict)
        #    self.application.jobs.append(job)

            #while not job.result:
            #    time.sleep(1)
            #
            #return_data['data'] = job.result
            #return_data['result'] = True
            #
            #print 'job complete'
            #print job.result

            #self.write_message(json.dumps(return_data))

        else:

            self.write_message(json.dumps(return_data))



        tornado.ioloop.IOLoop.instance().add_timeout(datetime.timedelta(seconds=1), self.check_queue)


    def check_queue(self):

        #print '.'
        list_to_remove = []

        for i in range(len(self.application.jobs)):

            j = self.application.jobs[i]

            j.refresh()

            print '\n***************************\n'

            print j.meta

            #from pprint import pprint
            #pprint (vars(j))

            if j.result:
                #print j.result
                print 'now removing it'
                list_to_remove.append(i)

                return_data = {}
                return_data['result'] = True
                return_data['func'] = 'update_image'
                return_data['contents'] = json.loads(j.result)

                self.write_message(json.dumps(return_data))


            elif j.meta:

                #todo add support for multiple jobs

                return_data = {}
                return_data['result'] = True
                return_data['func'] = 'update_meta'
                return_data['contents'] = j.meta

                self.write_message(json.dumps(return_data))


        for index in sorted(list_to_remove, reverse=True):
            print 'removing job at index %d' % index
            del self.application.jobs[index]

        #jobs_list = self.shared.q.get_jobs()
        #print self.shared.q.job_ids
        #print jobs_list
        #for n,j in enumerate(jobs_list):
        #    print n, j.result

        if len(self.application.jobs) > 0:
            tornado.ioloop.IOLoop.instance().add_timeout(datetime.timedelta(seconds=1), self.check_queue)


#tornado.ioloop.IOLoop.instance().add_timeout(datetime.timedelta(seconds=5), self.pollForAccessPoint)


#class UploadHandler(tornado.web.RequestHandler):
#
#    def post(self):
#        #print self.request.files.keys()
#        file1 = self.request.files['file'][0]
#        original_fname = file1['filename']
#        extension = os.path.splitext(original_fname)[1]
#        fname = ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(6))
#        final_filename= fname+extension
#        full_path = os.path.abspath(root) + "/static/uploads/" + final_filename
#        output_file = open(os.path.abspath(root) + "/static/uploads/" + final_filename, 'w')
#        output_file.write(file1['body'])
#        output_file.close()
#
#        from rqtasks import processImage
#        job = self.application.q.enqueue(processImage,full_path)
#        self.application.jobs.append(job)
#
#        self.finish("file" + final_filename + " is uploaded")




class GithubLoginHandler(BaseHandler, github.GithubMixin):

    #_OAUTH_REDIRECT_URL = 'http://localhost:8888/auth/github'
    _OAUTH_REDIRECT_URL = 'http://frontend.incfcloud.org/auth/github'

    @tornado.web.asynchronous
    def get(self):
        # we can append next to the redirect uri, so the user gets the
        # correct URL on login
        redirect_uri = tornado.httputil.url_concat(
                self._OAUTH_REDIRECT_URL, {'next': self.get_argument('next', '/')})

        # if we have a code, we have been authorized so we can log in
        if self.get_argument("code", False):

            print 'we have code'

            self.get_authenticated_user(
                redirect_uri=redirect_uri,
                client_id=self.settings["github_client_id"],
                client_secret=self.settings["github_secret"],
                code=self.get_argument("code"),
                callback=self.async_callback(self._on_login)
            )
            return



        # otherwise we need to request an authorization code
        self.authorize_redirect(
                redirect_uri=redirect_uri,
                client_id=self.settings["github_client_id"],
                extra_params={"scope": self.settings['github_scope'], "foo":1})


    def _on_login(self, user):
        """ This handles the user object from the login request """

        print('authenticated callback')

        #print user
        if user:
            logging.info('logged in user from github: ' + str(user))

            self.set_secure_cookie("user", tornado.escape.json_encode(user))

        else:
            self.clear_cookie("user")

        self.redirect(self.get_argument("next","/"))













class Application(tornado.web.Application):

    def __init__(self):

        parser = SafeConfigParser()
        parser.read('../settings.ini')

        gen_key = parser.get('admin', 'admin_generate_key')
        admin_key = ''

        if gen_key==1:
            import uuid
            admin_key = uuid.uuid4()
        else:
            admin_key = parser.get('admin', 'admin_key')

        self.jobs = []
        self.admin_key = str(admin_key)
        self.q = Queue(connection=Redis())

        print 'to access the admin path, visit /admin/%s' % (admin_key)

        handlers = [
            (r'/', WebHandler),
            (r'/ws', WSHandler),
            (r"/auth/github", GithubLoginHandler),
            (r'/logout', LogoutHandler)
            #(r"/auth/logout", AuthLogoutHandler),
            #(r'/upload', UploadHandler)
        ]
        settings = dict(
            cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",

            github_client_id="47663846f4ff92fbe8a3",
            github_secret="3ac166be872348f12c848c7dbe8e92b32e5803e9",

            github_scope = ['user','public_repo'],

            login_url="http://frontend.incfcloud.org/auth/github",

            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
        )
        tornado.web.Application.__init__(self, handlers, **settings)



 # Watch templates and static path directory
 #       for (path, dirs, files) in os.walk(settings["template_path"]):
 #           for item in files:
 #               tornado.autoreload.watch(os.path.join(path, item))
 #
 #       for (path, dirs, files) in os.walk(settings["static_path"]):
 #           for item in files:
 #               tornado.autoreload.watch(os.path.join(path, item))


def main():

    # I don't actually do anything here beyond configure port and allowable IPs
    tornado.options.parse_command_line()

    # init application
    app = Application()
    app.listen(options.port)

    # start the IO loop
    io_loop = tornado.ioloop.IOLoop.instance()
    #tornado.autoreload.start(io_loop)
    io_loop.start()

if __name__ == "__main__":
    main()
