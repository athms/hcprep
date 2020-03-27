#!/usr/bin/python
import numpy as np
import tensorflow as tf


def write_to_tfr(tfr_writers,
                 fMRI_data, volume_labels,
                 subject_id, task_id, run_id, n_classes_per_task,
                 randomize_volumes=True):
    """Writes fMRI volumes and labels to TFRecord files.

    Args:
        tfr_writers: A sequence of TFRecord writers to store the data
        fMRI_data: Ndarray of the fMRI volumes
        volume_labels: A sequence, containing one numeric label per 
            volume in fMRI_data
        subject_id: Integer ID of the subject that is stored in the
            TFR-files
        task_id: Integer ID of the HCP task that is stored in the 
            TFR-files
        run_id: Integer ID of the run that is stored  in the
            TFR-files
        n_classes_per_task: A sequence of integers indicating 
            the number of classes (ie., labels) per task in the
            HCP data. The overall number of classes determines
            the dimensionality of the one-hot label across tasks.
        randomize_volumes: Bool indicating whether the sequence of 
            volume (incl. their corresponding label) should be
            randomized before storing them in the TFR-files.

    Returns:
        None
    """
    X = np.array(fMRI_data)
    y = np.array(volume_labels)
    nx, ny, nz, nv = X.shape
    _vidx = np.arange(nv)
    if randomize_volumes:
        np.random.shuffle(_vidx)
    for vi in _vidx:
        try:
            writer = np.random.choice(tfr_writers)
            label = np.int(y[vi])
            label_onehot = [np.zeros(nc) for nc in n_classes_per_task]
            label_onehot[task_id][label] = 1
            label_onehot = np.concatenate(label_onehot)
            volume = np.array(X[:, :, :, vi].reshape(
                nx*ny*nz), dtype=np.float32)
            v_sample = tf.train.Example(
                features=tf.train.Features(
                    feature={'volume': tf.train.Feature(float_list=tf.train.FloatList(value=list(volume))),
                             'task_id': tf.train.Feature(int64_list=tf.train.Int64List(value=[np.int64(task_id)])),
                             'subject_id': tf.train.Feature(int64_list=tf.train.Int64List(value=[np.int64(subject_id)])),
                             'run_id': tf.train.Feature(int64_list=tf.train.Int64List(value=[np.int64(run_id)])),
                             'volume_idx': tf.train.Feature(int64_list=tf.train.Int64List(value=[np.int64(vi)])),
                             'label': tf.train.Feature(int64_list=tf.train.Int64List(value=[np.int64(label)])),
                             'label_onehot': tf.train.Feature(int64_list=tf.train.Int64List(value=list(label_onehot.astype(np.int64))))}))
            serialized = v_sample.SerializeToString()
            writer.write(serialized)
        except:
            continue


def parse_tfr(example_proto, nx, ny, nz, n_classes, only_parse_XY=False):
    """Parse TFR-data

    Args:
        example_proto: Single example from TFR-file
        nx, ny, nz: Integers indicating the x-/y-/z-dimensions
            of the fMRI data stored in the TFR-files
        n_classes: Total number of classes across tasks

    Returns:
        Parsed data stored in TFR-files. Specifically, the:

        volume: Ndarray of fMRI volume activations
        task_id: Integer ID of the HCP task 
        subject_id: Integer ID of the subject
        run_id: Integer ID of the run
        volume_idx: Integer sequence index of the fMRI volume
            in the original sequence of the data passed to
            hcprep.convert.write_to_tfr
        label: Integer label of the volume
        label_onehot: One-hot encoding of the label
        only_parse_XY: Bool indicating whether only volume 
            and y onehot encoding should be returned,
            as needed for integration with keras. If False,
            volume, task_id, subject_id, run_id, volume_idx,
            label, label_onehot are returned
    """
    features = {'volume': tf.FixedLenFeature([nx*ny*nz], tf.float32),
                'task_id': tf.FixedLenFeature([1], tf.int64),
                'subject_id': tf.FixedLenFeature([1], tf.int64),
                'run_id': tf.FixedLenFeature([1], tf.int64),
                'volume_idx': tf.FixedLenFeature([1], tf.int64),
                'label': tf.FixedLenFeature([1], tf.int64),
                'label_onehot': tf.FixedLenFeature([n_classes], tf.int64)}
    parsed_features = tf.parse_single_example(example_proto, features)
    volume_flat = parsed_features["volume"]
    volume = tf.reshape(volume_flat, [nx, ny, nz])
    label_onehot = parsed_features["label_onehot"]

    if only_parse_XY:
        return (volume, label_onehot)

    else:
        task_id = parsed_features['task_id']
        subject_id = parsed_features['subject_id']
        run_id = parsed_features['run_id']
        volume_idx = parsed_features['volume_idx']
        label = parsed_features["label"]
        return (volume,
                task_id,
                subject_id,
                run_id,
                volume_idx,
                label,
                label_onehot)
