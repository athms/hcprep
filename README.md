# HCPrep
HCPrep is a Python toolbox that allows to easily: 
1.  download the [Human Connectome Project](http://www.humanconnectomeproject.org) (HCP) [task-fMRI data](https://www.humanconnectome.org/study/hcp-young-adult/project-protocol/task-fmri) via the [Amazon S3 storage system](https://www.humanconnectome.org/study/hcp-young-adult/article/hcp-s1200-release-now-available-amazon-web-services) and 
2. preprocess these specifically for deep learning (DL) analyses with [tensorflow](https://www.tensorflow.org/).

HCPrep stores the data locally in the [Brain Imaging Data Structure](https://bids.neuroimaging.io) (BIDS) format.

To make the tfMRI data usable for DL analyses with tensorflow, HCPrep can also apply simple data cleaning steps to the downloaded task-fMRI data and store these in the [TFRecords format](https://www.tensorflow.org/tutorials/load_data/tfrecord).  

***NOTE: This project is still under development.***


## 1. Software Dependencies
HCPrep is written for Python 3.6 and requires a working Python environment running on your computer ([Anaconda Distribution](https://www.anaconda.com/distribution/) is recommended). You will also need to install [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html), [tensorflow (1.13)](https://www.tensorflow.org/install/pip), and [nilearn](https://nilearn.github.io/introduction.html#installing-nilearn). 

## 2. Getting Data Access
To download the data, you will also need AWS access to the HCP task-fMRI data directory. A detailed instruction can be found [here](https://wiki.humanconnectome.org/display/PublicData/How+To+Connect+to+Connectome+Data+via+AWS).

Make sure to safely store the `ACCESS_KEY` and `SECRET_KEY`. They are required to access the data via the AWS S3 storage system. 

## 3. AWS Configuration
Setup your local AWS client (as described [here](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html)). 

Add the following profile to '~/.aws/configure'

```bash
[profile hcp]
region=eu-central-1
```
Choose the region based on your [location](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.RegionsAndAvailabilityZones.html).

## 4. Basic Usage
HCPrep already contains the subject-IDs of 1000 participants for each of the seven task-fMRI tasks of the HCP task-fMRI data (see below). These can be found in the `subject_ids` directory. If more IDs are required, these can retrieved with the `retrieve_subject_ids` function of the `download` module. 

Overall, the task-fMRI data span the following seven tasks:

```python
tasks = ['EMOTION',
         'GAMBLING',
         'LANGUAGE',
         'MOTOR',
         'RELATIONAL',
         'SOCIAL',
         'WM']
 runs = ['LR', 'RL'] # two runs per task
 n_classes_per_task = [2, 3, 2, 5, 2, 2, 4] # number of decoding targets per task
```
For further details on the experimental tasks and their decoding targets (i.e., cognitive states), see [this](https://www.sciencedirect.com/science/article/abs/pii/S1053811913005272?via%3Dihub) and [this](https://arxiv.org/pdf/1907.01953.pdf).

### 4.1 Downloading the data
The task-fMRI data of a subject can be downloaded to a local machine as follows:

```python
import hcprep

task = 'WM'
task_id = 6 # 'WM' is the last of seven tasks
run = 'RL'
run_id = 1 # 'RL' is the second run
subject = '100307' # an example subject
output_path = 'data/' # path to store the downloaded data

hcprep.download.download_hcp_subject_data(ACCESS_KEY, SECRET_KEY, subject, task, run, output_path)
```

### 4.2 Interacting with the data
The HCPrep also contains a set of functions that allow to easily interact with the locally stored data in BIDS format. Specifically, each function returns the path of a filetype:

```python
# to get the path of the event files
hcprep.paths.path_bids_EV(subject, task, run, path)

# to get the path of the BOLD data in MNI space
hcprep.paths.path_bids_func_mni(subject, task, run, path)

# to get the path of the BOLD MASK in MNI space
hcprep.paths.path_bids_func_mask_mni(subject, task, run, path)
```

### 4.3 Cleaning the data
Once the task-fMRI data is downloaded you can clean it as follows:

```python
# load the subject data
subject_data = hcprep.data.load_subject_data(task, subject, run, path, TR)

# preprocess subject data
cleaned_fMRI, volume_labels = hcprep.preprocess.preprocess_subject_data(subject_data, [run], high_pass=1./128., smoothing_fwhm=3)
```
The cleaning steps are: detrending, frequency filtering, smoothing, and standardization of the voxel time series signals (as described in [Thomas et al. (2019)](https://www.frontiersin.org/articles/10.3389/fnins.2019.01321/full))

### 4.4 Writing the data to TFRecord files
Once the task-fMRI data is cleaned, you can easily write it to the TFRecord data format:

```python
import tensorflow as tf

# create a TFR-writer
n_tfr_writers = 1
tfr_writers = [tf.python_io.TFRecordWriter(
               tfr_path+'task-{}_subject-{}_run-{}_{}.tfrecords'.format(task, subject, run, wi))
               for wi in range(n_tfr_writers)]
               

# write preprocessed data to TFR
hcprep.convert.write_to_tfr(tfr_writers,
                            cleaned_fMRI.get_data(), volume_labels,
                            subject, task_id, run_id,
                            n_classes_per_task,
                            randomize_volumes=True)
```
