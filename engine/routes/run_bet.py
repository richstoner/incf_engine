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
    provgraph = bet_results.provenance

    vol = MapNode(fsl.ImageMaths(op_string='-sum'), iterfield=['in_file'],
                  name='volumeextractor')
    vol.inputs.in_file = bet_results.outputs.out_file
    vol.base_dir = workdir
    vol_results = vol.run()
    provgraph.add_bundle(vol_results.provenance)

    return provgraph, provgraph.rdf()


import hashlib
from utils import hash_infile, upload_graph

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
        select ?t1path ?sha where
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


    """
    Run bet and convert to rdf
    """
    provgraph, rdfgraph = run_bet(out_T1_files, cwd)

    # TODO: Need to reconcile rdfingraph and rdfgraph based on file hashes

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
