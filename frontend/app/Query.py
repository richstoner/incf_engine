# -*- coding: utf-8 -*-

import requests
import numpy as np

class Query(object):

    _sparqlXML = 'application/sparql-results+xml';
    _sparqlJSON = 'application/sparql-results+json';
    _rdfXML = 'application/rdf+xml';
    _rdfJSON = 'application/rdf+json';
    _rdfN3 = 'text/rdf+n3';
    _Html = 'text/html';

    def __init__(self, _endpoint='http://bips.incf.org:8890/sparql/', _defaultIRI='http://adhd200.gablab.mit.edu'):

        self.endpoint = _endpoint
        self.query = ''
        self.defaultIRI = _defaultIRI
        print 'Initialized as %s resource' % (self.endpoint)


    def subjectIDs(self):
        session = requests.Session()

        qstring = '''
            PREFIX fs: <http://freesurfer.net/fswiki/terms/>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            PREFIX nidm: <http://nidm.nidash.org/#>
            PREFIX prov: <http://www.w3.org/ns/prov#>

            SELECT DISTINCT ?id where {
                ?c1 fs:subject_id ?id .
            }
            '''
        session.headers = {'Accept':self._sparqlJSON} # HTML from SELECT queries
        data = {'query': qstring}
        result = session.post(self.endpoint, data=data)
        return_array = []
        for an in result.json()['results']['bindings']:
            return_array.append(an['id']['value'])
        return return_array


    def annotatedRegions(self):
        session = requests.Session()

        qstring = '''select distinct ?annotation where { ?s <http://nidm.nidash.org/terms/AnatomicalAnnotation> ?annotation} '''

        session.headers = {'Accept':self._sparqlJSON} # HTML from SELECT queries
        data = {'query': qstring}
        result = session.post(self.endpoint, data=data)
        return_array = []
        for an in result.json()['results']['bindings']:
            return_array.append(an['annotation']['value'])

        return return_array


    def computedMeasures(self):
        session = requests.Session()

        qstring = '''PREFIX fs: <http://freesurfer.net/fswiki/terms/>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            PREFIX nidm: <http://nidm.nidash.org/terms/>
            PREFIX prov: <http://www.w3.org/ns/prov#>

            select distinct ?measures
            where {
                   ?membersOfProvCollection a nidm:FreeSurferStatsCollection .
                   ?membersOfProvCollection prov:hadMember ?member .
                   ?member nidm:AnatomicalAnnotation fs:cuneus .
                   ?member ?measures ?o.
            }
            '''

        session.headers = {'Accept':self._sparqlJSON} # HTML from SELECT queries
        data = {'query': qstring}
        result = session.post(self.endpoint, data=data)
        return_array = []
        # print result.json()
        for an in result.json()['results']['bindings']:
            return_array.append(an['measures']['value'])

        return return_array


    def nidmTypes(self):
        session = requests.Session()
        qstring = '''

                PREFIX prov: <http://www.w3.org/ns/prov#>
                PREFIX obo: <http://purl.obolibrary.org/obo/>
                PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                PREFIX fs: <http://freesurfer.net/fswiki/terms/>
                PREFIX nidm: <http://nidm.nidash.org/terms/>
                PREFIX niiri: <http://nidm.nidash.org/iri/>
                PREFIX nif: <http://neurolex.org/wiki/>
                PREFIX dcterms: <http://purl.org/dc/terms/>

                SELECT DISTINCT ?Concept
                from <http://adhd200.nidm.org/>
                from <http://adhd200stats.nidm.org/>
                where {
                    ?s a ?Concept .
                }
            '''

        session.headers = {'Accept':self._sparqlJSON} # HTML from SELECT queries
        data = {'query': qstring, 'default-graph-uri': self.defaultIRI }

        result = session.post(self.endpoint, data=data)
        # print result.json()['results']

        # offset = len('http://freesurfer.net/fswiki/terms/')

        tags = []
        for concept in result.json()['results']['bindings']:
            v = concept['Concept']['value']
            tags.append(v)

        return tags



    def getJSforTitle(self, terms, title):
        return self._getJSfor(terms, title)

    def _getJSfor(self, terms, divname):

        terms.sort()

        options_all = ''
        for t in terms:
            options_all += '''<option value='%s'>%s</option>''' % (t,t)

        js = """
                container.show();
                var otherstring = $("<div><h4>%s</h4><select size=10 style='width:400px;' id='%s' multiple='multiple'>%s</select></div>");
                element.append(otherstring);
                """ % (divname, divname, options_all)

        return js

    def getJScallback(self, call_back_array, divname):

        js = """

        $("#%s").change(function(e){
            console.log($("#%s").val());
            kernel.execute("%s=" + JSON.stringify($("#%s").val()))
        });
        """ % (divname, divname, call_back_array, divname)

        return js


    def valueForAnnotationsMeasure(self, annotations, measure):
        session = requests.Session()

        qstring = '''
            PREFIX fs: <http://freesurfer.net/fswiki/terms/>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            PREFIX nidm: <http://nidm.nidash.org/terms/>
            PREFIX prov: <http://www.w3.org/ns/prov#>

            select ?sid ?annotation ?measure ?obotest
            where {
                   ?membersOfProvCollection a nidm:FreeSurferStatsCollection .
                   ?membersOfProvCollection prov:wasDerivedFrom ?statEntity .
                   ?statEntity nidm:AnatomicalAnnotation ?obotest .
                   ?directoryCollection prov:hadMember ?statEntity .
                   ?directoryCollection fs:subject_id ?sid .
                   ?membersOfProvCollection prov:hadMember ?member .
                   ?member nidm:AnatomicalAnnotation ?annotation.
                   ?member <%s> ?measure .
                   filter regex(?obotest, '281') .

                   }
        ''' % (measure)

        print qstring

        session.headers = {'Accept':self._sparqlJSON} # HTML from SELECT queries
        data = {'query': qstring}
        result = session.post(self.endpoint, data=data)

        # return result.json()['results']['bindings']

        return_dict = {}

        subject_list = []
        annotation_list = []

        # print result.json()['results']['bindings'][0:10]

        for an in result.json()['results']['bindings']:

            annotation = an['annotation']['value']

            if annotation in annotations:

                print annotation
                measure = float(an['measure']['value'])

                hemi = 1
                if '2812' in an['obotest']['value']:
                    hemi = 0

                sid = an['sid']['value']

                if sid not in return_dict.keys():
                    sdict = {}
                    sdict['l'] = {}
                    sdict['r'] = {}

                    if hemi == 0:
                        sdict['r'][annotation] = measure
                    else:
                        sdict['l'][annotation] = measure
                        return_dict[sid] = sdict
                else:
                    sdict = return_dict[sid]

                    if hemi == 0:
                        sdict['r'][annotation] = measure
                    else:
                        sdict['l'][annotation] = measure

                    return_dict[sid] = sdict

        return return_dict
            # if sid not in subject_list:
            #     subject_list.append(sid)

            # if annotation in annotations:
            #     return_array.append([sid, annotation, measure, hemi])





        # return [return_array, subject_list, annotations]

        #
        # ad = np.empty([len(annotation_list), len(subject_list)], dtype=float)
        #
        # print(ad.shape)
        #
        # lastSub = ''
        # subIndex = 0
        #
        # for d in return_array:
        #
        #     if lastSub != d[0]:
        #         lastSub = d[0]
        #         subIndex += 1
        #
        #     ad[0][subIndex - 1] = d[0]
        #     ad[1][subIndex -1] = d[3]
        #
        #     region_index = annotation_list.index(d[1]) + 2
        #
        #     ad[region_index][subIndex - 1] = d[2]
        #
        # return ad



























    def listTypesInGraph(self):
        session = requests.Session()
        qstring = '''
            
            PREFIX fs: <http://freesurfer.net/fswiki/terms/>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            PREFIX nidm: <http://nidm.nidash.org/#>
            PREFIX prov: <http://www.w3.org/ns/prov#>

            select distinct ?Concept where { [] a ?Concept .
            filter regex(?Concept, "http://freesurfer.net/fswiki/terms" ) }
            '''

        session.headers = {'Accept':self._sparqlJSON} # HTML from SELECT queries
        data = {'query': qstring, 'default-graph-uri': self.defaultIRI } 

        result = session.post(self.endpoint, data=data)
        # print result.json()['results']

        offset = len('http://freesurfer.net/fswiki/terms/')

        tags = []
        for concept in result.json()['results']['bindings']:
            v = concept['Concept']['value'][offset:]
            tags.append(v)

        return tags








    def listPredicatesInGraph(self):
        session = requests.Session()

        qstring = '''

            PREFIX fs: <http://freesurfer.net/fswiki/terms/>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            PREFIX nidm: <http://nidm.nidash.org/#>
            PREFIX prov: <http://www.w3.org/ns/prov#>

            select distinct ?p where { ?s ?p ?o. filter regex(?p, "http://freesurfer.net/fswiki/terms") }
            '''

        session.headers = {'Accept':self._sparqlJSON}   # HTML from SELECT queries
        data = {'query': qstring, 'default-graph-uri': self.defaultIRI }
        result = session.post(self.endpoint, data=data)

        offset = len('http://surfer.nmr.mgh.harvard.edu/fswiki/#')

        tags = []
        for concept in result.json()['results']['bindings']:
            v = concept['p']['value'][offset:]
            tags.append(v)

        return tags


        # return result.json()['results']['bindings']

    def getSubjectDetails(self, subject_id):
        session = requests.Session()

        qstring = '''

        PREFIX fs: <http://surfer.nmr.mgh.harvard.edu/fswiki/#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX nidm: <http://nidm.nidash.org/#>
        PREFIX prov: <http://www.w3.org/ns/prov#>

        select distinct ?structureName ?structureGV where {
             ?subjectCollection fs:subject_id "%s"^^<http://www.w3.org/2001/XMLSchema#string> .
             ?subjectCollection prov:hadMember ?otherMembers .
             ?collectionFromProv prov:wasDerivedFrom ?otherMembers .
             ?collectionFromProv prov:hadMember ?membersOfProvCollection .
             ?membersOfProvCollection a fs:GrayVol . # filter by those that have a type of fs:GrayVol(ume)
             ?membersOfProvCollection fs:structure ?structureName . 
             ?membersOfProvCollection fs:value ?structureGV .
             
        } ''' % (subject_id)

        session.headers = {'Accept':self._sparqlJSON} # HTML from SELECT queries
        data = {'query': qstring}
        result = session.post(self.endpoint, data=data)
        return result.json()['results']['bindings']












    def getData(self, structure='BA'):
        session = requests.Session()

        qstring = '''
            PREFIX fs: <http://surfer.nmr.mgh.harvard.edu/fswiki/#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            PREFIX nidm: <http://nidm.nidash.org/#>
            PREFIX prov: <http://www.w3.org/ns/prov#>

            select distinct $id $structure $volume $hemi where {
                ?c1 nidm:annotation "adhd200"^^xsd:string .
                ?c1 fs:subject_id ?id .
                ?c1 prov:hadMember ?f .
                ?f fs:hemisphere ?hemi .
                ?c prov:wasDerivedFrom ?f .
                ?c prov:hadMember ?s .
                ?s a fs:GrayVol .
                ?s fs:structure ?structure .
                ?s fs:value ?volume .
                FILTER regex(str(?structure), "%s")
            }
        ''' % structure

        session.headers = {'Accept':self._sparqlJSON} # HTML from SELECT queries
        data = {'query': qstring}
        result = session.post(self.endpoint, data=data)

        return_array = []
        for an in result.json()['results']['bindings']:
            return_array.append(an['annotation']['value'])

        return return_array



    def buildQueryForFiltered(self, concept_dict, predicate_dict):
        
        session = requests.Session()
        qstring = '''
            PREFIX fs: <http://surfer.nmr.mgh.harvard.edu/fswiki/#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            PREFIX nidm: <http://nidm.nidash.org/#>
            PREFIX prov: <http://www.w3.org/ns/prov#>

            select distinct $id $structure $volume $hemi where {
                ?c1 nidm:annotation "adhd200"^^xsd:string .
                ?c1 fs:subject_id ?id .
                ?c1 prov:hadMember ?f .
                ?f fs:hemisphere ?hemi .
                ?c prov:wasDerivedFrom ?f .
                ?c prov:hadMember ?s .
                ?s a fs:GrayVol .
                ?s fs:structure ?structure .
                ?s fs:value ?volume .
                FILTER regex(str(?structure), "%s")
            }
        ''' % structure

        session.headers = {'Accept':self._sparqlJSON} # HTML from SELECT queries
        data = {'query': qstring}
        result = session.post(self.endpoint, data=data)
        return result.json()['results']['bindings']







    def getFileURLforFile(self, filelocation):

        import requests
        resolvestring = filelocation
        # print resolvestring
        r = requests.get(resolvestring)
        return r.json()



    # def getXTKViewForSubject(self, subject_id):
    #     session = requests.Session()

    #     qstring = '''
    #         PREFIX fs: <http://surfer.nmr.mgh.harvard.edu/fswiki/#> 
    #         PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> 
    #         PREFIX nidm: <http://nidm.nidash.org/#>
    #         PREFIX prov: <http://www.w3.org/ns/prov#>

    #         select distinct ?id ?file where {
    #                         ?c1 nidm:annotation "adhd200"^^xsd:string .
    #                         ?c1 fs:subject_id "%s"^^<http://www.w3.org/2001/XMLSchema#string> .
    #                         ?c1 prov:hadMember ?e .
    #                         ?e  fs:hemisphere "left"^^xsd:string .
    #                         ?e  nidm:file ?file .
    #                         FILTER regex(?file, "surf/.h.pial")
    #         }
    #     ''' % subject_id

    #     session.headers = {'Accept':self._sparqlJSON} # HTML from SELECT queries
    #     data = {'query': qstring}
    #     result = session.post(self.endpoint, data=data)
    #     return result.json()['results']['bindings']

    def getFileForSubject(self, file_name, subject_id):
        session = requests.Session()

        qstring = '''

            PREFIX prov: <http://www.w3.org/ns/prov#>
            PREFIX fs: <http://freesurfer.net/fswiki/terms/>
            PREFIX crypto: <http://www.w3.org/2000/10/swap/crypto#>
            PREFIX nidm: <http://nidm.nidash.org/terms/>

            select ?locations where
            {
                ?subject fs:subject_id "%s" .
                ?subject prov:hadMember ?members .
                ?members prov:location ?locations .

                FILTER regex(?locations, "%s")
            }
            '''% (subject_id, file_name)

        session.headers = {'Accept':self._sparqlJSON} # HTML from SELECT queries
        data = {'query': qstring}

        result = session.post(self.endpoint, data=data)

        return result.json()['results']['bindings']            
        
    def getBoundsFromData(self, data):
        import numpy as np

        # each region will become a coordinate
        # each id will become a coordinate
        # left hemisphere first

        listOfRegions = []
        listOfsubjects = []

        for d in data:
            if d['structure']['value'] not in listOfRegions:
                listOfRegions.append(d['structure']['value'])
            if d['id']['value'] not in listOfsubjects:
                listOfsubjects.append(d['id']['value'])

        return [listOfRegions, listOfsubjects]


    def buildJSONArray(self, data, listOfRegions, listOfsubjects):
        print(len(listOfRegions))
        # 9 regional volumes, 2 per subject id (left/right)
        ad = np.empty((11, len(listOfsubjects)))
        print(ad.shape)

        # 11 total fields: subid, left/right, regional volumes
        lastSub = ''
        subIndex = 0

        for d in data:
            if lastSub != d['id']['value']:
                lastSub = d['id']['value']
                subIndex += 1
            
            ad[0][subIndex - 1] = int(d['id']['value'])
            
            if d['hemi']['value'] == 'left':
                ad[1][subIndex -1] = 0
            else:
                ad[1][subIndex -1] = 1
                
            region_index = listOfRegions.index(d['structure']['value']) + 2
            
            ad[region_index][subIndex - 1] = float(d['volume']['value'])

        return ad


    def getD3pc(self, graphid, datastr):

        js = """
        container.show();

        var xtkdiv = $('<div id="%s" class="parcoords" style="width:800px;" height:500px;"></div>');
        xtkdiv.css('background-color','#fff');
        element.append(xtkdiv);
        console.log('eh');

        var blue_to_brown = d3.scale.linear()
          .domain([0, 1])
          .range(["steelblue", "brown"])
          .interpolate(d3.interpolateLab);

        var color = function(d) { return blue_to_brown(d[1]); };

        var brushListener = function(event) { 
            kernel.execute("brushed_selection=" + JSON.stringify(event))
            };

        d3.parcoords()("#%s")
            .data(%s)
            .color(color)
            .alpha(0.4)
            .render()
            .mode("queue")
            .shadows()
            .brushable()  // enable brushing
            .on('brush', brushListener);

        // load csv file and create the chart
        //d3.csv('files/cars.csv', function(data) {
        //}); 

        """ % (graphid, graphid, datastr)

        return js

    def getSlick(self, graphid):

        js = '''

        var xtkdiv = $('<div id="%s" class="parcoords" style="width:1500px;height:500px"></div>');
        xtkdiv.css('background-color','#f00');
        element.append(xtkdiv);


        var griddiv = $('<div id="grid" ></div>');
        
        griddiv.css('background-color','#a00');
        element.append(griddiv);
        
        var pagerdiv = $('<div id="pager" ></div>');
        element.append(pagerdiv);
        pagerdiv.css('background-color','#60');


        });''' % (graphid)

        return js

# http://computor.mit.edu:10101/file?file_uri=file://computor.mit.edu/mindhive/xnat/surfaces/adhd200/2570769/surf/lh.curv.pial


    # def convertToArray(self, arrayToConvert):
    #     labelarray = []
    #     valuearray = np.zeros(len(jsongraph['bindings']), dtype='f')
    #     indarray = np.arange(len(jsongraph['bindings']))
                                           

    #     for n,val in enumerate(jsongraph['bindings']):
    #     #    data_to_plot.append([val['structureName']['value'], float(val['structureGV']['value'])])
    #         labelarray.append(val['structureName']['value'])
    #         valuearray[n] = float(val['structureGV']['value'])



# select distinct $id $w $x where {
#                 ?c1 nidm:annotation "sad"^^xsd:string .
#                 ?c1 fs:subject_id ?id .
#                 ?c1 prov:hadMember ?f .
#                 ?c prov:wasDerivedFrom ?f .
#                 ?c prov:hadMember ?s .
#                 ?s a ?m .
#                 ?s fs:structure ?w .
#                 ?s fs:value ?x 
#                 FILTER regex(str(?m), fs:ICV)
# }

# get all subject ids

