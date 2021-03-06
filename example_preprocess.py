#!/usr/bin/python
import os
import argparse
import numpy as np
import tensorflow as tf
import hcprep


if __name__ == "__main__":

    # setup parser
    ap = argparse.ArgumentParser()
    # add arguments to parser
    ap.add_argument("--path", required=False,
                    help="path to local BIDS data")
    args = vars(ap.parse_args())
    # set variables
    if args['path'] is not None:
        path = str(args['path'])
        print('Path: {}'.format(path))
    else:
        path = 'data/'
        print('"path" not defined. Defaulting to: {}'.format(path))
    
    # extract subject IDs
    subjects = [int(f.split('sub-')[1])
                for f in os.listdir(path) if 'sub' in f]

    # HCP data information
    hcp_info = hcprep.info.basics()

    # tfr path
    tfr_path = path+'tfr/'
    hcprep.paths.make_sure_path_exists(tfr_path)

    # write data
    print('Processing these tasks: {}, with each {} subjects and {} runs.\n'.format(
        hcp_info.tasks, len(subjects), len(hcp_info.runs)))
    for subject_id, subject in enumerate(subjects):
        print('Processing subject: {}/{}'.format(subject_id+1, len(subjects)))
        for task_id, task in enumerate(hcp_info.tasks):
            for run_id, run in enumerate(hcp_info.runs):
                # create TFR-writers
                tfr_writers = [tf.python_io.TFRecordWriter(
                    tfr_path+'task-{}_subject-{}_run-{}.tfrecords'.format(
                        task, subject, run))]
                # load subject data
                subject_data = hcprep.data.load_subject_data(
                    task, subject, [run], path, hcp_info.t_r)
                # preprocess subject data
                volumes, volume_labels = hcprep.preprocess.preprocess_subject_data(
                    subject_data, [run], high_pass=1./128., smoothing_fwhm=3)
                # write preprocessed data to TFR
                hcprep.convert.write_to_tfr(tfr_writers,
                                            volumes.get_data(),
                                            volume_labels,
                                            subject_id,
                                            task_id,
                                            run_id,
                                            hcp_info.n_classes_per_task,
                                            randomize_volumes=True)
                # close writers
                [w.close() for w in tfr_writers]
