Engine API Core
---------------

Implementation of the engine's core API for submitting and managing jobs on
the network.

## API Resources

### JobsList

* Resource Path `/jobs`
* GET - provides a list of jobs in the queue
* POST - submit a graph to be operated on

### Jobs

* Resource `/jobs/<id>`
* GET
* POST - updates or modifications of a job resource
* PUT - new jobs or completely replacing a resource
* DELETE

### FilesList

* Resource Path `/files`
* GET /files

### Files

* Resource Path `/files/<id>`
* GET /files

### SERVICES

* GET - list of services
* Post - register a service
