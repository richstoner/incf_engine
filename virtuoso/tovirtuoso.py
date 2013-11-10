__author__ = 'satra'

import rdflib
import requests

query1 = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX fs: <http://freesurfer.net/fswiki/terms/>
PREFIX nidm: <http://nidm.nidash.org/terms/>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX niiri: <http://nidm.nidash.org/iri/>
PREFIX obo: <http://purl.obolibrary.org/obo/>
PREFIX nif: <http://neurolex.org/wiki/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX crypto: <http://www.w3.org/2000/10/swap/crypto#>

select ?id { ?c1 fs:subject_id ?id }

"""

query2 = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX fs: <http://freesurfer.net/fswiki/terms/>
PREFIX nidm: <http://nidm.nidash.org/terms/>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX niiri: <http://nidm.nidash.org/iri/>
PREFIX obo: <http://purl.obolibrary.org/obo/>
PREFIX nif: <http://neurolex.org/wiki/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX crypto: <http://www.w3.org/2000/10/swap/crypto#>

construct {
?c a prov:Agent;
    nidm:id "%s";
    nidm:Age ?age ;
    nidm:Verbal_IQ ?viq ;
    nidm:DX ?dx .
?e1 a prov:Entity;
      prov:wasAttributedTo ?c;
           a nif:nlx_inv_20090243;
           crypto:sha ?sha;
           prov:location "http://192.168.100.20/file/%s_anat_1.nii.gz";
           prov:location "s3://adhd200/data/%s_anat_1.nii.gz" .
}
where
{?c fs:subject_id "%s" .
  ?c prov:hadMember ?e1 .
  ?e1 prov:label ?label ;
      crypto:sha ?sha .
  FILTER(regex(?label, "001.mgz"))
SERVICE <http://computor.mit.edu:8890/sparql> {
           ?c2 nidm:ID "%s" .
           ?c2 nidm:Age ?age .
           ?c2 nidm:Verbal_IQ ?viq .
           ?c2 nidm:DX ?dx .
      }
}
"""

endpoint1 = 'http://metadata.incf.org:8890/sparql'
endpoint2 = 'http://192.168.100.30:8890/sparql'

g = rdflib.ConjunctiveGraph('SPARQLStore')
g.open(endpoint1)
results = g.query(query1)
count = 0
for row in results:
    count += 1
    sid = str(row[0])
    if len(sid) < 7:
        continue
    query = query2 % (sid, sid, sid, sid, sid)
    sidgraph = g.query(query)
    print sidgraph.serialize(format='turtle')
    # session defaults
    session = requests.Session()
    session.headers = {'Accept':'text/html'} # HTML from SELECT queries

    query = """
    INSERT IN GRAPH <http://sfndemo.nidm.org>
    {
    %s
    }
    """ % sidgraph.serialize(format='nt')
    print query
    data = {'query': query}
    #result = session.post(endpoint2, data=data)

