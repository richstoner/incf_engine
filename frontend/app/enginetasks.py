import requests
import os
#import numpy as np
import urllib
#import matplotlib.pyplot as plt
#from scipy import ndimage
#from scipy import misc
#from skimage import filter
import json

import time

# queue utilities
from rq import get_current_job
import socket
#
#
#def processDropboxImage(files):
#
#    job = get_current_job()
#
#    job.meta['handled_by'] = socket.gethostname()
#    job.meta['state'] = 'start'
#    job.save()
#
#    print 'Current job: %s' % (job.id)
#    #print job.meta
#
#    for file in files:
#
#        import uuid
#        url_to_grab = file['link']
#        image_path = '/vagrant/app/static/uploads/%s%s' % (uuid.uuid4(), os.path.splitext(file['link'])[1])
#
#        urllib.urlretrieve(url_to_grab,image_path)
#        job.meta['state'] = 'download complete'
#        job.save()
#        #time.sleep(3)
#
#        im = ndimage.imread(image_path, True)
#
#        job.meta['state'] = 'image loaded complete'
#        job.save()
##        time.sleep(3)
#
#        edges2 = filter.canny(im, sigma=3)
#
#        job.meta['state'] = 'filter complete'
#        job.save()
#        #time.sleep(3)
#
#        misc.imsave(image_path[:-4] + '-canny.jpg', edges2)
#
#        job.meta['state'] = 'image saved'
#        job.save()
#        #time.sleep(3)
#
#        return_data = {}
#        return_data['processed'] = image_path[:-4] + '-canny.jpg'
#        return_data['original'] = image_path
#        return_data['src'] = '/static/uploads/%s' % os.path.split(return_data['original'])[1]
#        return_data['srcproc'] = '/static/uploads/%s' % os.path.split(return_data['original'])[1][:-4] + '-canny.jpg'
#        #return_data['callback_id'] = callback_id
#        #print job.meta
#
#        return json.dumps(return_data)
#
#
#def processImage(image_path):
#
#    #job = get_current_job()
#    #
#    #job.meta['handled_by'] = socket.gethostname()
#    #job.save()
#
#    im = ndimage.imread(image_path, True)
#    edges2 = filter.canny(im, sigma=3)
#    misc.imsave(image_path[:-4] + '-canny.jpg', edges2)
#
#    return_data = {}
#    return_data['processed'] = image_path[:-4] + '-canny.jpg'
#    return_data['original'] = image_path
#    return_data['src'] = '/static/uploads/%s' % os.path.split(return_data['original'])[1]
#    return_data['srcproc'] = '/static/uploads/%s' % os.path.split(return_data['original'])[1][:-4] + '-canny.jpg'
#
#    #return_data['callback_id'] = callback_id
#    return json.dumps(return_data)
#    #return 3
#    #return image_path[:-4] + '-canny.jpg'
#
#
#def processT1(t1_filename):
#
#    import os
#
#    import nipype.pipeline.engine as pe
#    import nipype.interfaces.io as nio
#    from nipype.interfaces.freesurfer.preprocess import ReconAll
#    from nipype.interfaces.freesurfer.utils import MakeAverageSubject
#
#    subject_list = ['s1', 's3']
#    data_dir = os.path.abspath('data')
#    subjects_dir = os.path.abspath('amri_freesurfer_tutorial/subjects_dir')
#
#    wf = pe.Workflow(name="l1workflow")
#    wf.base_dir = os.path.abspath('amri_freesurfer_tutorial/workdir')
#
#    datasource = pe.MapNode(interface=nio.DataGrabber(infields=['subject_id'],
#                                                      outfields=['struct']),
#                            name='datasource',
#                            iterfield=['subject_id'])
#    datasource.inputs.base_directory = data_dir
#    datasource.inputs.template = '%s/%s.nii'
#    datasource.inputs.template_args = dict(struct=[['subject_id', 'struct']])
#    datasource.inputs.subject_id = subject_list
#
#
#    recon_all = pe.MapNode(interface=ReconAll(), name='recon_all',
#                           iterfield=['subject_id', 'T1_files'])
#    recon_all.inputs.subject_id = subject_list
#    if not os.path.exists(subjects_dir):
#        os.mkdir(subjects_dir)
#    recon_all.inputs.subjects_dir = subjects_dir
#
#    wf.connect(datasource, 'struct', recon_all, 'T1_files')
#
#
#    average = pe.Node(interface=MakeAverageSubject(), name="average")
#    average.inputs.subjects_dir = subjects_dir
#
#    wf.connect(recon_all, 'subject_id', average, 'subjects_ids')
#
#    wf.run("MultiProc", plugin_args={'n_procs': 4})
#
#
#    #print 'test'
#
#    #from nipype.interfaces.freesurfer import ReconAll
#    #reconall = ReconAll()
#    #reconall.inputs.subject_id = 'foo'
#    #reconall.inputs.directive = 'all'
#    #reconall.inputs.subjects_dir = '.'
#    #reconall.inputs.T1_files = t1_filename
#    #print reconall.cmdline
#    #return json.dumps(reconall.cmdline)
#
#    #return 't1val'
#    #import nipype.pipeline.engine as pe
#    #import nipype.interfaces.io as nio
#    #
#    #import os
#    #
#    ## We need freesurfer's recon-all utility
#    #from nipype.interfaces.freesurfer.preprocess import ReconAll
#    #
#    ## Our subjects directories
#    #subject_list = ['1031', '1032']
#    #
#    ## Their location
#    #data_dir = os.path.abspath('data')
#    #
#    ## Subjects directory (our working directory?)
#    #subjects_dir = os.path.abspath('/usr/local/freesurfer/subjects')
#    #
#    ## Generate a workflow and specify the location for temporary storage of files
#    #wf = pe.Workflow(name="l1workflow")
#    #wf.base_dir = os.path.abspath('/usr/local/freesurfer/subjects')
#    #
#    #
#    ## Generate the first (map-)node, datasource, which will run the subject_ids in
#    ## parallel
#    ##  The inputs it expects are called subject_id and the outputs it hands down are
#    ##  called struct
#    #datasource = pe.MapNode(interface=nio.DataGrabber(infields=['subject_id'], outfields=['struct']), name='datasource', iterfield=['subject_id'])
#    #
#    ## Specify how and from where datasource should get its input (via DataGrabber)
#    #datasource.inputs.base_directory = data_dir
#    ## Typical file name: (/usr/local/freesurfer/data/)1031/struct.nii
#    #datasource.inputs.template = '%s/%s.nii'
#    #datasource.inputs.template_args = dict(struct=[['subject_id', 'struct']])
#    ## To be used in iterfield, etc
#    #datasource.inputs.subject_id = subject_list
#    #
#    ## Generate the second (map-)node, recon_all, which will run the subject_ids in
#    ## parallel. ...and all T1 files of given subject | spit out multiple T1 files?
#    ## --FIXME-- is the above description correct?
#    #recon_all = pe.MapNode(interface=ReconAll(), name='recon_all', iterfield=['subject_id', 'T1_files'])
#    #
#    ## Specify how recon_all should get its input and where it should save its files
#    ## --FIXME-- is that correct?
#    #recon_all.inputs.subject_id = subject_list
#    #if not os.path.exists(subjects_dir):
#    #    os.mkdir(subjects_dir)
#    #recon_all.inputs.subjects_dir = subjects_dir
#    #
#    ## Connect both nodes to the workflow and name the information that flows between
#    ## them (struct, T1_files)
#    #wf.connect(datasource, 'struct', recon_all, 'T1_files')
#    #
#    ## Run our workflow (distribute it across 4 CPU nodes)
#    #wf.run("MultiProc", plugin_args={'n_procs': 4})
#
#



def count_words_at_url(url):
    resp = requests.get(url)
    return len(resp.text.split())