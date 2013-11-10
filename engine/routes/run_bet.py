#!/usr/bin/env python
"""Run FreeSurfer on a T1 image and capture all output as NIDM
"""
import os

import urllib
import urlparse
from StringIO import StringIO

from nipype.interfaces.base import CommandLine
CommandLine.set_default_terminal_output('allatonce')

from nipype import config
config.enable_provenance()

import rdflib

def run_bet(T1_image, workdir):
    """Run freesurfer, convert to nidm and extract stats
    """
    from nipype import fsl
    from nipype import MapNode

    strip = MapNode(fsl.BET(), iterfield=['in_file'], name='skullstripper')
    strip.inputs.in_file = T1_image
    strip.inputs.mesh = True
    strip.inputs.mask = True
    strip.base_dir = workdir

    bet_results = strip.run()
    provgraph = bet_results.provenance[0]
    for bundle in bet_results.provenance[1:]:
        provgraph.add_bundle(bundle)

    vol = MapNode(fsl.ImageStats(op_string='-V'), iterfield=['in_file'],
                  name='volumeextractor')
    vol.inputs.in_file = bet_results.outputs.out_file
    vol.base_dir = workdir
    vol_results = vol.run()
    for bundle in vol_results.provenance:
        provgraph.add_bundle(bundle)

    return provgraph, provgraph.rdf()


import hashlib
from utils import hash_infile, upload_graph, prov

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(prog='fs_dir_to_graph.py',
                                     description=__doc__)
    parser.add_argument('-i', '--in_graph', type=str, required=True,
                        help='Path to input graph turtle file')
    parser.add_argument('-e', '--endpoint', type=str,
                        help='SPARQL endpoint to use for update')
    parser.add_argument('-g', '--graph_iri', type=str,
                        help='Graph IRI to store the triples')

    args = parser.parse_args()

    cwd = os.getcwd()

    rdfingraph = rdflib.Graph().parse(args.in_graph, format='turtle')

    """
    Parse the input graph to get subject id and a list of T1 files

    """
    t1_query = """
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX nif: <http://neurolex.org/wiki/>
        PREFIX crypto: <http://www.w3.org/2000/10/swap/crypto#>
        select ?t1path ?sha ?e where
        {?e a prov:Entity;
            a nif:nlx_inv_20090243;
            crypto:sha ?sha;
            prov:location ?t1path .
            FILTER(regex(?t1path, "http*"))
        }
    """
    t1_result = rdfingraph.query(t1_query)

    """
    Retrieve the file into wd
    """
    out_T1_files = []
    filemap = {}
    for idx, info in enumerate(t1_result.bindings):
        o = urlparse.urlparse(info['?t1path'])
        if o.scheme.startswith('file'):
            uri = 'file://' + o.path
        else:
            uri = info['?t1path']
        filename = os.path.join(cwd,
                                'file_%d_' % idx + os.path.split(o.path)[-1])
        urllib.urlretrieve(uri, filename)
        if hash_infile(filename, crypto=hashlib.sha512) != str(info['?sha']):
            raise IOError("Hash of file doesn't match remote hash")
        out_T1_files.append(filename)
        filemap[filename] = (info['?sha'], info['?e'])

    """
    Run bet and convert to rdf
    """
    provgraph, rdfgraph = run_bet(out_T1_files, cwd)

    nipype_files = """
PREFIX nipype: <http://nipy.org/nipype/terms/>
select ?e ?value where {
     ?e a prov:Entity ;
        nipype:value ?value .
        FILTER(regex(?value, 'file://'))
}
    """
    filesfound = rdfgraph.query(nipype_files)

    for info in filesfound.bindings:
        localfile = urlparse.urlparse(info['?value']).path
        relpath = localfile.replace(cwd, cwd.rstrip('/').split('/')[-1])
        print localfile, relpath
        sha = hash_infile(localfile, crypto=hashlib.sha512)
        if localfile in filemap:
            rdfgraph.add((rdflib.URIRef(info['?e']),
                          rdflib.URIRef(prov.PROV['wasDerivedFrom'].get_uri()),
                          rdflib.URIRef(filemap[localfile][1])))
        rdfgraph.add((rdflib.URIRef(info['?e']),
                      rdflib.URIRef('http://www.w3.org/2000/10/swap/crypto#sha'),
                      rdflib.Literal(sha)))
        rdfgraph.add((rdflib.URIRef(info['?e']),
                      rdflib.URIRef(prov.PROV['location'].get_uri()),
                      rdflib.Literal('http://192.168.100.20/file/%s' %
                                     relpath, datatype=rdflib.XSD['anyURI'])))

    newgraph = rdflib.Graph().parse(StringIO(rdfgraph.serialize()))
    newgraph.serialize(os.path.join(cwd, 'outfile.ttl'), format='turtle')

    context = {('@%s' % k): v for k, v in newgraph.namespaces()}
    newgraph.serialize('outfile.json', context=context, format='json-ld')

    if args.endpoint:
        if args.graph_iri:
            upload_graph(newgraph, endpoint=args.endpoint,
                         graph_iri=args.graph_iri)
        else:
            upload_graph(newgraph, endpoint=args.endpoint)
