
Uses [Vagrant](http://www.vagrantup.com/) for development
so everyone on your team has the exact same environment.

[Ansible](http://www.ansibleworks.com/docs/) to provision
Vagrant and other environments.

[Flask-SQLAlchemy](http://pythonhosted.org/Flask-SQLAlchemy/)
is also included to handle all database (PostgresSQL) interactions.

The skeleton is engineered to run on any Debian/Ubuntu based system,
while remaining compatible with Heroku. It splits up its web and database
components allowing you to scale up with ease.

Really Quick Start
-------------------

Make sure you have Vagrant and Ansible installed.

Get a development environment running:

	$ vagrant up web
	$ vagrant ssh
	$ cd /srv/flask_skeleton && python main.py
	Open http://192.168.100.10

Put it in production:

	Edit ops/vars.yml
	Edit ops/hosts
	$ ./deploy.sh

Or deploy to Heroku as you normally would.


Instructions
------------

First, you'll need to clone the repo.

    $ git clone https://github.com/nickhs/flask_skeleton.git
    $ cd flask_skeleton

Then you'll need to downloand and install [Vagrant](http://www.vagrantup.com/)
if you don't have it already. You'll also need [VirtualBox](https://www.virtualbox.org/wiki/Downloads)
or an alternative Vagrant provider.

   http://downloads.vagrantup.com/

You'll also need to have [Ansbile](http://www.ansibleworks.com/docs/gettingstarted.html)
(the provisioning mechanism) installed. The easiest method is to do:

	$ sudo pip install ansible

Don't have pip? You can grab it with:

	$ sudo easy_install pip

Finally let Vagrant do the rest. Don't worry if it seems noisy:

	$ vagrant up db
	$ vagrant up web
	$ vagrant ssh web
	$ cd /srv/flask_skeleton
	$ python main.py

Visit the site at [192.168.100.10](http://192.168.100.10).

Deploying to a box
-------------------

Deploying your application to your
EC2/Linode/DigitalOcean/server somewhere is a cinch.

If you don't already have Ansbile, the provisioning system,
you'll need to [download it](http://www.ansibleworks.com/docs/gettingstarted.html#getting-ansible).

Your easiest bet is to install it via `pip`:

	$ sudo pip install ansible

Make sure you edit the `ops/vars.yml` file to specify the application name,
repository location and generate secret keys and database passwords.

Add the server(s) in `ops/hosts`, note this is an
[Ansible hosts file](http://www.ansibleworks.com/docs/patterns.html/#list-of-reserved-inventory-parameters)
and you can pass the relevant parameters accordingly.

For example your hosts file could look like this:

	# Production webservers go here
	[webservers]
	web1.server.com ansible_ssh_user=ubuntu ansible_ssh_private_key_file=~/secrets/main.pem

	# Production databases go here
	# Want just one box? Make them the same
	[dbservers]
	db.server.com ansible_ssh_user=ubuntu ansible_ssh_private_key_file=~/secrets/main.pem

	[production:children]
	dbservers
	webservers

If you want everything on the same box just enter the same host under both sections. Don't want a database? Leave the dbservers
section blank.

Once you're done defining your hosts do:

    $ ./deploy.sh

Note: `./deploy.sh` is idempotent, don't be afraid to run it over and over again.

From then on out to just update the code you can do:

    $ ./deploy.sh --fast

Deploying to Heroku
-------------------

Make sure you have the [`heroku`
Ruby gem](http://devcenter.heroku.com/articles/using-the-cli) installed.

If you haven't [signed up for Heroku](https://api.heroku.com/signup), go
ahead and do that. You should then be able to [add your SSH key to
Heroku](http://devcenter.heroku.com/articles/quickstart), and also
`heroku login` from the commandline.

Now, to upload your application, you'll first need to do the
following -- and obviously change `app_name` to the name of your
application:

    $ heroku create app_name -s cedar

And, then you can push your application up to Heroku.

    $ git push heroku master
    $ heroku scale web=1

Finally, we can make sure the application is up and running.

    $ heroku ps

Now, we can view the application in our web browser.

    $ heroku open


Next Steps
----------

After you've got your application up and running, there a couple next
steps you should consider following.

1. Create a new `README.md` file.
2. Add your Google Analytics ID to the `base.html` template.
3. Adjust the `author` and `description` `<meta>` tags in the
   `base.html` template.
4. Change the `humans.txt` and `favicon.ico` files in the `static`
   directory.
5. Change the `apple-touch` icons in the `static` directory.


Heroku Custom Domains
--------------

If your account is verified -- and your credit card is on file -- you
can also easily add a custom domain to your application.

    $ heroku addons:add custom_domains
    $ heroku domains:add www.mydomainname.com

You can add a [naked domain
name](http://devcenter.heroku.com/articles/custom-domains), too.

    $ heroku domains:add mydomainname.com

Lastly, add the following A records to your DNS management tool.

    75.101.163.44
    75.101.145.87
    174.129.212.2

Shout Outs
-----------

Based on the amazing work of both https://github.com/zachwill/flask_heroku
and https://github.com/mattupstate/vagrant-ansible-tutorial
