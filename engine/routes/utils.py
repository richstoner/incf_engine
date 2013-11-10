__author__ = 'satra'

import hashlib
import os
from uuid import uuid1

# PROV API library
import prov.model as prov
import rdflib

# create namespace references to terms used
foaf = prov.Namespace("foaf", "http://xmlns.com/foaf/0.1/")
dcterms = prov.Namespace("dcterms", "http://purl.org/dc/terms/")
fs = prov.Namespace("fs", "http://freesurfer.net/fswiki/terms/")
nidm = prov.Namespace("nidm", "http://nidm.nidash.org/terms/")
niiri = prov.Namespace("niiri", "http://iri.nidash.org/")
obo = prov.Namespace("obo", "http://purl.obolibrary.org/obo/")
nif = prov.Namespace("nif", "http://neurolex.org/wiki/")
crypto = prov.Namespace("crypto", "http://www.w3.org/2000/10/swap/crypto#")

get_id = lambda : niiri[uuid1().hex]

def hash_infile(afile, crypto=hashlib.md5, chunk_len=8192):
    """ Computes hash of a file using 'crypto' module"""
    hex = None
    if os.path.isfile(afile):
        crypto_obj = crypto()
        fp = file(afile, 'rb')
        while True:
            data = fp.read(chunk_len)
            if not data:
                break
            crypto_obj.update(data)
        fp.close()
        hex = crypto_obj.hexdigest()
    return hex

def upload_graph(graph, endpoint=None, graph_iri='http://sfndemo.nidm.org'):
    import requests
    from requests.auth import HTTPDigestAuth

    # connection params for secure endpoint
    if endpoint is None:
        endpoint = 'http://metadata.incf.org:8890/sparql'

    # session defaults
    session = requests.Session()
    session.headers = {'Accept': 'text/html'}  # HTML from SELECT queries

    counter = 0
    max_stmts = 1000
    stmts = graph.rdf().serialize(format='nt').splitlines()
    N = len(stmts)
    while (counter < N):
        endcounter = min(N, counter + max_stmts)
        query = """
        INSERT IN GRAPH <%s>
        {
        %s
        }
        """ % (graph_iri, '\n'.join(stmts[counter:endcounter]))
        data = {'query': query}
        result = session.post(endpoint, data=data)
        print(result)
        counter = endcounter
    print('Submitted %d statemnts' % N)

def check_graph(graph):
    newg = rdflib.Graph()
    try:
        for stmt in graph:
            newg.add(stmt)
            rdflib.Graph().parse(data=newg.serialize(format='turtle'),
                                 format='turtle')
    except:
        print stmt
