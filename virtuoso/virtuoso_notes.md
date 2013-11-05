### Notes

Virtuoso still uses a commandline config tool to set the root password.

Once the instance is up, ssh in 

	vagrant ssh virtuoso

Reconfigure the package

	sudo dpkg-reconfigure -plow virtuoso-opensource-6.1
	
Update the service config: change 'run=no' to 'run=YES'

	sudo pico /etc/default/virtuoso-opensource-6.1
	
Start virtuoso

	sudo service virtuoso-opensource-6.1 start
	

Now you can visit the Virtuoso page at [http://192.168.100.30:8890](http://192.168.100.30:8890)


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


(Instructions valid as of 11/4/13 - RMS)