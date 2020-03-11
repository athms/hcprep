#!/usr/bin/python
import os
import argparse
import numpy as np
import hcprep


if __name__ == '__main__':

    # setup parser
    ap = argparse.ArgumentParser()
    # add arguments to parser
    ap.add_argument("--ACCESS_KEY", required=True,
                    help="AWS S3 access key")
    ap.add_argument("--SECRET_KEY", required=True,
                    help="AWS S3 secret key")
    ap.add_argument("--path", required=False,
                    help="output path to store data")
    ap.add_argument("--n_subjects", required=False,
                    help="number of subjects to download per HCP task")
    args = vars(ap.parse_args())
    # set variables
    ACCESS_KEY = str(args['ACCESS_KEY'])
    SECRET_KEY = str(args['SECRET_KEY'])
    if args['path'] is not None:
        output_path = str(args['path'])
        print('Path: {}'.format(output_path))
    else:
        output_path = 'data/'
        print('"path" not defined. Defaulting to: {}'.format(output_path))
    hcprep.paths.make_sure_path_exists(output_path)
    if args['n_subjects'] is not None:
        n_subjects = int(args['n_subjects'])
    else:
        n_subjects = 2
    print('n_subjects to download: {}'.format(n_subjects))

    # HCP exp. descriptors
    tasks = ['EMOTION',
             'GAMBLING',
             'LANGUAGE',
             'MOTOR',
             'RELATIONAL',
             'SOCIAL',
             'WM']
    runs = ['LR', 'RL']

    # download subject data
    for task in tasks:
        task_subjects = np.load(
            'subject_ids/tfMRI_{}_subject_ids.npy'.format(task))[:n_subjects]
        for subject in task_subjects:
            for run in runs:
                hcprep.download.download_hcp_subject_data(
                    ACCESS_KEY, SECRET_KEY, subject, task, run, output_path)
