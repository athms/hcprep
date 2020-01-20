# tfMRI_HCP_downloader

This is a small Python toolbox to download the Human Connectome Project (HCP) task-fMRI data via the Amazon S3 storage system.

Note that the toolbox with store the data locally in the [Brain Imaging Data Structure](https://bids.neuroimaging.io)(BIDS) format.

## Installation

The tfMRI-HCP_downloader is written for Python 3.7 and requires a working Python environment running on your computer. We recommend to install the [Anaconda Distribution](https://www.anaconda.com/distribution/) (available for all major platforms). You will also need to install [Boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)

## Getting Data Access

Before using the downloader, you will also need to request access to the HCP tfMRI data. A detailed instruction, can be found [here](https://wiki.humanconnectome.org/display/PublicData/How+To+Connect+to+Connectome+Data+via+AWS).

Make sure to store the ACCESS_KEY and SECRET_KEY. You need these to access the HCP data via the AWS S3 storage system. 

## Basic Usage

The toolbox contains files with the subject-IDs of 1000 participants for each of the seven tfMRI tasks of the HCP data. These can be founde in the subject_ids directory.

The tfMRI data of a subject can be downloaded to a local machine as follows:

```bash
import tfMRI_HCP_downloader

task = 'WM'
run = 'RL'
subject = '381038'
output_path = 'data'

tfMRI_HCP_downloader.download.download_hcp_subject_data(ACCESS_KEY, SECRET_KEY, subject, task, run, output_path)

```

The tfMRI-HCP_downloader also contains a set of simple functions that allows you to interact with the locally stored data in BIDS format. Specifically, each function returns the path of a filetype:

```bash

task = 'WM'
run = 'RL'
subject = '381038'
path = 'data'

# to get the path of the event files
tfMRI_HCP_downloader.path.path_bids_EV(subject, task, run, path)

# to get the path of the BOLD data in MNI space
tfMRI_HCP_downloader.path.path_bids_func_mni(subject, task, run, path)

# to get the path of the BOLD MASK in MNI space
tfMRI_HCP_downloader.path.path_bids_func_mask_mni(subject, task, run, path)
```
