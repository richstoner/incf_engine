### Notes

The Virtuoso database is configured with a default password and allows data to be inserted without authenticatication

**Once running, change the `dba` user password**

The default password is:

    username: dba
    password: dba

You can change the password by logging into the machine, or through the user interface

#### By Logging In

Once the instance is up, you can ssh in 

	vagrant ssh virtuoso

Reconfigure the package

	sudo dpkg-reconfigure -plow virtuoso-opensource-6.1

You will be prompted to change the default password

#### By User Interface

Visit the [Conductor Web App](http://192.168.100.30:8890/conductor)
	

By default the Virtuoso page is at [http://192.168.100.30:8890](http://192.168.100.30:8890)

### Configuration Notes from Vagrant

**Note: this information is already configured - No Action Necessary**
	
Enable Running w/o a password

Update the service config: change 'run=no' to 'run=YES'

	sudo pico /etc/default/virtuoso-opensource-6.1

### To Enable Write Permissions Using SPARQL Update (SPARUL)

Log into the Virtuoso iSQL terminal
	
	isql-vt

Execute the following from the terminal:

	grant SPARQL_UPDATE to "SPARQL";
	quit();

Now you can insert data via the Virtuoso SPARQL Query Interface at [http://192.168.100.30:8890/sparql](http://192.168.100.30:8890/sparql)

### Example Inserting Data Using SPARQL
	
	PREFIX ex: <http://example.com/>

	CREATE GRAPH <http://example.com/>
	INSERT INTO <http://example.com/> { ex:subject ex:predicate "object" . }
	
You can then query the data you have entered:

	SELECT *
	FROM <http://example.com/>
	WHERE {?s ?p ?o .}

As well as clear the graph of data, and drop the graph itself:
	
	CLEAR GRAPH <http://example.com/>
	DROP GRAPH <http://example.com/>

**note: SPARUL will only support up to 10000 lines of code at a time**

Starting virtuoso

	sudo service virtuoso-opensource-6.1 start

Stopping virtuoso

	sudo service virtuoso-opensource-6.1 stop


(Instructions valid as of 11/10/13 - nicholsn)