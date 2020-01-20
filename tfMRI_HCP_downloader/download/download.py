#!/usr/bin/python
import sys
import os
import numpy as np
import boto3

from ._utils import make_sure_path_exists, return_hcp_EV_file_ids


def connect_to_hcp_bucket(ACCESS_KEY, SECRET_KEY):
    boto3.setup_default_session(profile_name='hcp',
                                aws_access_key_id=ACCESS_KEY,
                                aws_secret_access_key=SECRET_KEY,
                                region_name='us-east-1')
    s3 = boto3.resource('s3')
    bucket = s3.Bucket('hcp-openaccess')
    return bucket


def retrieve_hcp_tfMRI_subject_ids(ACCESS_KEY, SECRET_KEY, task, runs=['LR', 'RL'], n=1000):
    bucket = connect_to_hcp_bucket(
        ACCESS_KEY=ACCESS_KEY, SECRET_KEY=SECRET_KEY)
    subject_ids = []
    sample_key = ('/MNINonLinear/' +
                  'Results/' +
                  'tfMRI_{}_RL/'.format(task) +
                  'tfMRI_{}_RL.nii.gz'.format(task))
    for o in bucket.objects.filter(Prefix='HCP'):
        if (sample_key in o.key):
            subject = o.key.split('/')[1]
            if check_subject_data_present(bucket, subject, task, runs):
                if subject not in subject_ids:
                    subject_ids.append(subject)
        if len(subject_ids) >= n:
            break
    return subject_ids


def check_subject_data_present(bucket, subject, task, runs):
    checks = []
    for run in runs:
        prefix = 'HCP/{}/MNINonLinear/Results/tfMRI_{}_{}/'.format(
            subject, task, run)
        # tfMRI data
        tfMRI_key = (prefix+'tfMRI_{}_{}.nii.gz'.format(task, run))
        checks.append(check_key_exists(tfMRI_key, bucket, prefix))

        # tfMRI mask
        tfMRI_mask_key = (prefix + 'brainmask_fs.2.nii.gz')
        checks.append(check_key_exists(tfMRI_mask_key, bucket, prefix))

        # EV data
        for EV_file in return_hcp_EV_file_ids(task):
            EV_key = (prefix+'EVs/'+EV_file)
            checks.append(check_key_exists(EV_key, bucket, prefix))

    if np.sum(checks) == len(checks):
        return True
    else:
        return False


def download_hcp_subject_data(ACCESS_KEY, SECRET_KEY, subject, task, run, output_path):

    # make sure all requiered dirs exist
    path_sub = output_path+'sub-{}/'.format(subject)
    path_anat = path_sub+'anat/'
    path_func = path_sub+'func/'
    make_sure_path_exists(path_sub)
    make_sure_path_exists(path_anat)
    make_sure_path_exists(path_func)

    # connect to S3 bucket
    bucket = connect_to_hcp_bucket(
        ACCESS_KEY=ACCESS_KEY, SECRET_KEY=SECRET_KEY)

    # tfMRI data
    bucket_id = ('HCP/{}/'.format(subject) +
                 'MNINonLinear/' +
                 'Results/' +
                 'tfMRI_{}_{}/'.format(task, run) +
                 'tfMRI_{}_{}.nii.gz'.format(task, run))
    output_file = path_func+'sub-{}_task-{}_run-{}_bold.nii.gz'.format(
        subject, task, run)
    if not os.path.isfile(output_file):
        print('downloading file: {}  to  {}'.format(bucket_id, output_file))
        bucket.download_file(bucket_id, output_file)
        print('done.')

    # brainmaks
    bucket_id = ('HCP/{}/'.format(subject) +
                 'MNINonLinear/' +
                 'Results/' +
                 'tfMRI_{}_{}/'.format(task, run) +
                 'brainmask_fs.2.nii.gz')
    output_file = path_func+'sub-{}_task-{}_run-{}_brainmask.nii.gz'.format(
        subject, task, run)
    if not os.path.isfile(output_file):
        print('downloading file: {}  to  {}'.format(bucket_id, output_file))
        bucket.download_file(bucket_id, output_file)
        print('done.')

    # EV data
    identifier = ('HCP/{}/'.format(subject) +
                  'MNINonLinear/' +
                  'Results/' +
                  'tfMRI_{}_{}/'.format(task, run) +
                  'EVs/')
    for EV_file in return_hcp_EV_file_ids(task):
        bucket_id = identifier+EV_file
        output_file = path_func+'sub-{}_task-{}_run-{}_EV-{}'.format(
            subject, task, run, EV_file)
        if not os.path.isfile(output_file):
            print('downloading file: {}  to  {}'.format(bucket_id, output_file))
            bucket.download_file(bucket_id, output_file)
            print('done.')
