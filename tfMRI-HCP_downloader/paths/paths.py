#!/usr/bin/python

def path_bids_EV(subject, task, run, path):
    return path+'sub-{}/func/sub-{}_task-{}_run-{}_EV-summary.csv'.format(
        subject, subject, task, run)

def path_bids_func_mni(subject, task, run, path):
    return path+'sub-{}/func/sub-{}_task-{}_run-{}_bold.nii.gz'.format(
        subject, subject, task, run)

def path_bids_func_mask_mni(subject, task, run, path):
    return path+'sub-{}/func/sub-{}_task-{}_run-{}_brainmask.nii.gz'.format(
        subject, subject, task, run)
