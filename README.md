# HCPrep
HCPrep is a Python toolbox that allows to easily download the **preprocessed** [Human Connectome Project](http://www.humanconnectomeproject.org) (HCP) [task-fMRI data](https://www.humanconnectome.org/study/hcp-young-adult/project-protocol/task-fmri) via the [Amazon Web Services (AWS) S3 storage system](https://www.humanconnectome.org/study/hcp-young-adult/article/hcp-s1200-release-now-available-amazon-web-services).

HCPrep stores the data locally in the [Brain Imaging Data Structure](https://bids.neuroimaging.io) (BIDS) format.

To make the tfMRI data usable for DL analyses with tensorflow, HCPrep can also apply simple data cleaning steps to the downloaded task-fMRI data and store these in the [TFRecords format](https://www.tensorflow.org/tutorials/load_data/tfrecord).  

```diff
- NOTE: THIS PROJECT IS STILL UNDER DEVELOPMENT.
```

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
All necessary descriptive information about the HCP task-fMRI data is contained in `info.basics`:

```python
hcp_info = hcprep.info.basics()
```

`basics` contains the following information:
- `tasks`: names of all HCP fMRI tasks ('EMOTION', 'GAMBLING', 'LANGUAGE', 'MOTOR', 'RELATIONAL', 'SOCIAL', 'WM')
- `classes_per_task`: dictionary containing names of each class (ie., cognitive state) within each task
- `subjects`: dictionary containing 1000 subject IDs for each task
- `runs`: task-fMRI run IDs ('LR', 'RL')
- `t_r`: repetition time of the fMRI data in seconds (0.72)

For further details on the experimental tasks and their decoding targets (i.e., cognitive states), see [this](https://www.sciencedirect.com/science/article/abs/pii/S1053811913005272?via%3Dihub) and [this](https://arxiv.org/pdf/1907.01953.pdf).

If more subject IDs are required, these can be retrieved by the use of the `retrieve_subject_ids` function of the `download` module.

### 4.1 Downloading the data
The task-fMRI data of a subject can be downloaded to a local machine as follows:

```python
import hcprep

task = 'WM' # working memory task (WM)
run = hcp_info.runs[0] # the first run
subject = hcp_info.subjects[task][0] # the first subject of the WM task
output_path = 'data/' # path to store the downloaded data

hcprep.download.download_subject_data(ACCESS_KEY, SECRET_KEY,
                                      subject=subject,
                                      task=task,
                                      run=run,
                                      output_path=output_path)
```

### 4.2 Interacting with the data
HCPrep also contains a set of functions that allow to easily interact with the locally stored data in BIDS format. Specifically, each function returns the path of one of the tfMRI filetypes:

```python
# to get the path of the event files
hcprep.paths.path_bids_EV(subject=subject, task=task, run=run, path=path)

# to get the path of the BOLD data in MNI space
hcprep.paths.path_bids_func_mni(subject=subject, task=task, run=run, path=path)

# to get the path of the BOLD MASK in MNI space
hcprep.paths.path_bids_func_mask_mni(subject=subject, task=task, run=run, path=path)
```

### 4.3 Cleaning the data
Once the task-fMRI data is downloaded you can clean it as follows:

```python
# load the subject data
subject_data = hcprep.data.load_subject_data(task=task,
                                             subject=subject,
                                             run=run,
                                             path=path,
                                             t_r=hcp_info.t_r)

# preprocess subject data
cleaned_fMRI, volume_labels = hcprep.preprocess.preprocess_subject_data(
         subject_data=subject_data, runs=[run], high_pass=1./128., smoothing_fwhm=3)
```
The cleaning steps are derived from [nilearn](https://nilearn.github.io/modules/generated/nilearn.signal.clean.html) and include:
1. Linear detrending of the voxel time series signals
2. Frequency filtering of the voxel time series signals
3. Spatial smoothing with a Gaussian kernel
4. Standardization of the voxel time series signals to have a mean of 0 and unit variance (as described in [Thomas et al. (2019)](https://www.frontiersin.org/articles/10.3389/fnins.2019.01321/full))

### 4.4 Writing the data to TFRecord files
Once the task-fMRI data is cleaned, you can easily write it to the TFRecord data format:

```python
import tensorflow as tf

# the task and run are encoded numerically in the TFR-files
task_id = np.where(hcp_info.tasks==task)[0][0] # 6: 'WM' is the last of out of all seven tasks in hcp_info.tasks
run_id = np.where(hcp_info.runs==run)[0][0] # 0: 'LR' is the first run in hcp_info.runs

# create a TFR-writer
tfr_writers = [tf.python_io.TFRecordWriter(
               tfr_path+'task-{}_subject-{}_run-{}.tfrecords'.format(task, subject, run)]
               

# write preprocessed data to TFR
hcprep.convert.write_to_tfr(tfr_writers=tfr_writers,
                            fMRI_data=cleaned_fMRI.get_data(),
                            volume_labels=volume_labels,
                            subject_id=subject,
                            task_id=task_id,
                            run_id=run_id,
                            n_classes_per_task=hcp_info.n_classes_per_task, # a list of the number of classes for each task
                            randomize_volumes=True)
```
The resulting TFRecords file contains one entry for each input fMRI volume with the following features:
- "volume": the flattened voxel activations of shape 91 x 109 x 91 (flattened over the X, Y, and Z dimensions)
- "task_id", "subject_id", "run_id"
- "volume_idx": the time series index of the volume in the input fMRI data
- "label": the label of the volume within its task (for example [0,1,2,3] for the WM task)
- "label_onehot": one-hot encoding of the label across all tasks (length determined by sum over n_classes_per_task)

### 4.5 Reading TFRecord files

Lastly, you can read the data from the TFRecord files by the use of hcprep's ```parse_tfr``` function. For more information on how to build data queues with TFRecords files and to integrate them in your workflow, see [here](https://www.tensorflow.org/tutorials/load_data/tfrecord) and [here](https://medium.com/@moritzkrger/speeding-up-keras-with-tfrecord-datasets-5464f9836c36). 

This is a quick example of how to setup a data queue:

```python
batch_size = 8 # batch size 
n_queue_workers = 1 # number of workers used to parse tfr data (see below)
with tf.variable_scope('data_queue'): # create tf variable scope

    # define a placeholder for the TFRecord filenames that later will be parsed
    filenames = tf.placeholder(tf.string, shape=[None])
    
    # setup a TFRecord dataset instance
    dataset = tf.data.TFRecordDataset(filenames)
    
    # pool-map for the dataset and parse function
    dataset = dataset.map(
        lambda x: hcprep.convert.parse_tfr(
        x, nx=nx, ny=ny, nz=nz, n_classes=n_classes,
        only_return_XY=False), n_queue_workers)
        
    # ignore errors, e.g., when the queued files do not
    # contain enough entries to fill up the next batch
    dataset = dataset.apply(tf.data.experimental.ignore_errors())
    
    # specify the batch size
    dataset = dataset.batch(batch_size)
    
    # repeat the dataset for training
    dataset = dataset.repeat()
    
    # create an iterator
    iterator = dataset.make_initializable_iterator()
    # get tensors for parsed batch data
    (tfr_volume,
     tfr_task_id,
     tfr_subject_id,
     tfr_run_id,
     tfr_volume_idx,
     tfr_label,
     tfr_label_onehot) = iterator.get_next()
```

In this example, you can then use ```tfr_volume``` and ```tfr_label_onehot``` to train your deep learning model.

Note that ```parse_tfr``` also contains a switch ("only_return_XY") to only return the parsed ```tfr_volume``` and ```tfr_label_onehot``` for easier integration of the TFRecordDataset queue with Keras.
