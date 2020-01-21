#!/usr/bin/python
import os
import argparse
import numpy as np
import tensorflow as tf
import tfMRI_HCP_downloader


if __name__ == "__main__":

    # retrieve ACCESS KEY & SECRET KEY
    ap = argparse.ArgumentParser()
    # add arguments to parser
    ap.add_argument("--path", required=False,
                    help="AWS S3 access key")
    ap.add_argument("--n_tfr", required=False,
                    help="AWS S3 access key")
    args = vars(ap.parse_args())
    # set variables
    if args['path'] is not None:
        path = str(args['path'])
        print('Path: {}'.format(path))
    else:
        path = 'data/'
        print('"path" not defined. Defaulting to: {}'.format(path))
    if args['n_tfr'] is not None:
        n_tfr_writers = int(args['n_tfr'])
    else:
        n_tfr_writers = 1
    print(
        'Number of TFR-writers per [task, subject, run]: {}'.format(n_tfr_writers))

    # extract subject IDs
    subjects = [int(f.split('sub-')[1])
                for f in os.listdir(path) if 'sub' in f]

    # HCP exp. descriptors
    TR = 0.72  # TR in seconds
    tasks = ['EMOTION',
             'GAMBLING',
             'LANGUAGE',
             'MOTOR',
             'RELATIONAL',
             'SOCIAL',
             'WM']
    runs = ['LR', 'RL']
    # number of decoding targets per task
    n_classes_per_task = [2, 3, 2, 5, 2, 2, 4]

    # tfr path
    tfr_path = path+'tfr/'
    tfMRI_HCP_downloader.paths.make_sure_path_exists(tfr_path)

    # write data
    for subject_id, subject in enumerate(subjects):
        print('Processing subject: {}/{}'.format(subject_id+1, len(subjects)))
        for task_id, task in enumerate(tasks):
            for run_id, run in enumerate(runs):
                # create TFR-writers
                tfr_writers = [tf.python_io.TFRecordWriter(
                    tfr_path+'task-{}_subject-{}_run-{}_{}.tfrecords'.format(task, subject, run, wi))
                    for wi in range(n_tfr_writers)]
                # load subject data
                subject_data = tfMRI_HCP_downloader.data.load_subject_data(
                    task, subject, run, path, TR)
                # preprocess subject data
                volumes, volume_labels = tfMRI_HCP_downloader.preprocess.preprocess_subject_data(
                    subject_data, [run], high_pass=1./128., smoothing_fwhm=3)
                # write preprocessed data to TFR
                tfMRI_HCP_downloader.convert.write_to_tfr(tfr_writers,
                                                          volumes.get_data(), volume_labels,
                                                          subject_id, task_id, run_id, n_classes_per_task,
                                                          randomize_volumes=True)
                # close writers
                [w.close() for w in tfr_writers]
