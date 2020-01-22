#!/usr/bin/python
import os


def make_sure_path_exists(path):
	"""Make sure a path exists.
	If it does not exist, create it.
	"""
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


def path_bids_EV(subject, task, run, path):
	"""Return the path to the local EV-summary
	file of a subject in a task run.

	Args:
		subject: Integer ID of HCP subject
        task: String ID of HCP task.
        runs: String ID of HCP run (one of ["LR", "RL"])
        path: Path to local BIDS directory.
	"""
    return path+'sub-{}/func/sub-{}_task-{}_run-{}_EV-summary.csv'.format(
        subject, subject, task, run)


def path_bids_func_mni(subject, task, run, path):
	"""Return the path to the local task-fMRI data
	of a subject in a task run.

	Args:
		subject: Integer ID of HCP subject
        task: String ID of HCP task.
        runs: String ID of HCP run (one of ["LR", "RL"])
        path: Path to local BIDS directory.
	"""
    return path+'sub-{}/func/sub-{}_task-{}_run-{}_bold.nii.gz'.format(
        subject, subject, task, run)


def path_bids_func_mask_mni(subject, task, run, path):
	"""Return the path to the local task-fMRI brainmask
	of a subject in a task run.

	Args:
		subject: Integer ID of HCP subject
        task: String ID of HCP task.
        runs: String ID of HCP run (one of ["LR", "RL"])
        path: Path to local BIDS directory.
	"""
    return path+'sub-{}/func/sub-{}_task-{}_run-{}_brainmask.nii.gz'.format(
        subject, subject, task, run)
