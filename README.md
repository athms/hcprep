# dlprep_tfMRI_HCP

dlprep_tfMRI_HCP is a Python toolbox to download the [Human Connectome Project](http://www.humanconnectomeproject.org) (HCP) [task-fMRI](https://www.humanconnectome.org/study/hcp-young-adult/project-protocol/task-fmri) data via the Amazon S3 storage system and to preprocess is specifically for deep learning analyses with tensorflow.

dlprep_tfMRI_HCP stores the data locally in the [Brain Imaging Data Structure](https://bids.neuroimaging.io) (BIDS) format.

To make the tfMRI data usable for DL analyses with tensorflow, tfMRI_HCP_downloader further applies simple data cleaning to the downloaded tfMRI data and stores these in the [TFRecords format](https://www.tensorflow.org/tutorials/load_data/tfrecord).  

**NOTE: This project is still under development.**

## Installation

dlprep_tfMRI_HCP is written for Python 3.6 and requires a working Python environment running on your computer. We recommend to install the [Anaconda Distribution](https://www.anaconda.com/distribution/) (available for all major platforms). You will also need to install [Boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html), [tensorflow (1.13)](https://www.tensorflow.org/install/pip), and [nilearn](https://nilearn.github.io/introduction.html#installing-nilearn). 

## Getting Data Access

Before downloading the data, you will need to request AWS access to the HCP tfMRI data. A detailed instruction can be found [here](https://wiki.humanconnectome.org/display/PublicData/How+To+Connect+to+Connectome+Data+via+AWS).

Make sure to safely store the ACCESS_KEY and SECRET_KEY. You need these to later access the data via the AWS S3 storage system. 

## AWS configuration

Setup your local AWS client (as described [here](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html)). 

Add the following profile to '~/.aws/configure'

```bash
[profile hcp]
region=eu-central-1
```

Choose the region based on your [location](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.RegionsAndAvailabilityZones.html).

## Basic Usage

dlprep_tfMRI_HCP already contains .npy-files with the subject-IDs of 1000 participants for each of the seven tfMRI tasks of the HCP tfMRI data. These can be found in the subject_ids directory.

The tfMRI data of a subject can be downloaded to a local machine as follows:

```bash
import tfMRI_HCP_downloader

task = 'WM'
run = 'RL'
subject = '381038'
output_path = 'data'

dlprep_tfMRI_HCP.download.download_hcp_subject_data(ACCESS_KEY, SECRET_KEY, subject, task, run, output_path)

```

The dlprep_tfMRI_HCP also contains a set of functions that allow to easily interact with the locally stored data in BIDS format. Specifically, each function returns the path of a filetype:

```bash

# to get the path of the event files
dlprep_tfMRI_HCP.paths.path_bids_EV(subject, task, run, path)

# to get the path of the BOLD data in MNI space
dlprep_tfMRI_HCP.paths.path_bids_func_mni(subject, task, run, path)

# to get the path of the BOLD MASK in MNI space
dlprep_tfMRI_HCP.paths.path_bids_func_mask_mni(subject, task, run, path)
```

Once the data is downloaded, you can preprocess and convert it to the TFRecords file format as follows:

```bash
# create a TFR-writer
n_tfr_writers = 1
tfr_writers = [tf.python_io.TFRecordWriter(
               tfr_path+'task-{}_subject-{}_run-{}_{}.tfrecords'.format(task, subject, run, wi))
               for wi in range(n_tfr_writers)]

# load the subject data
subject_data = dlprep_tfMRI_HCP.data.load_subject_data(task, subject, run, path, TR)

# preprocess subject data
volumes, volume_labels = dlprep_tfMRI_HCP.preprocess.preprocess_subject_data(
subject_data, [run], high_pass=1./128., smoothing_fwhm=3)

# write preprocessed data to TFR
dlprep_tfMRI_HCP.convert.write_to_tfr(tfr_writers,
                                      volumes.get_data(), volume_labels,
                                      subject_id, task_id, run_id, n_classes_per_task,
                                      randomize_volumes=True)
```
