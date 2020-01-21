#!/usr/bin/python
import numpy as np
import tensorflow as tf


def write_to_tfr(tfr_writers,
                 fMRI_data, volume_labels,
                 subject_id, task_id, run_id, n_classes_per_task,
                 randomize_volumes=True):
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
            label_indicator = [np.zeros(nc) for nc in n_classes_per_task]
            label_indicator[task_tfr_id][label] = 1
            label_indicator = np.concatenate(label_indicator)
            volume = np.array(X[:, :, :, vi].T.reshape(
                nx*ny*nz), dtype=np.float32)
            v_sample = tf.train.Example(
                features=tf.train.Features(
                    feature={'volume': tf.train.Feature(float_list=tf.train.FloatList(value=list(volume))),
                             'task_id': tf.train.Feature(int64_list=tf.train.Int64List(value=[np.int64(task_id)])),
                             'subject_id': tf.train.Feature(int64_list=tf.train.Int64List(value=[np.int64(subject_id)])),
                             'run_id': tf.train.Feature(int64_list=tf.train.Int64List(value=[np.int64(run_id)])),
                             'volume_idx': tf.train.Feature(int64_list=tf.train.Int64List(value=[np.int64(vi)])),
                             'label': tf.train.Feature(int64_list=tf.train.Int64List(value=[np.int64(label)])),
                             'label_indicator': tf.train.Feature(int64_list=tf.train.Int64List(value=list(label_indicator.astype(np.int64))))}))
            serialized = v_sample.SerializeToString()
            writer.write(serialized)
        except:
            continue


def parse_tfr(example_proto, nx, ny, nz, n_classes):
    features = {'volume': tf.FixedLenFeature([nx*ny*nz], tf.float32),
                'task_id': tf.FixedLenFeature([1], tf.int64),
                'subject_id': tf.FixedLenFeature([1], tf.int64),
                'run_id': tf.FixedLenFeature([1], tf.int64),
                'volume_idx': tf.FixedLenFeature([1], tf.int64),
                'label': tf.FixedLenFeature([1], tf.int64),
                'label_indicator': tf.FixedLenFeature([n_classes], tf.int64)}
    parsed_features = tf.parse_single_example(example_proto, features)

    volume_flat = parsed_features["volume"]
    volume = tf.reshape(volume_flat, [nz, ny, nx])

    task_id = parsed_features['task_id']
    subject_id = parsed_features['subject_id']
    run_id = parsed_features['run_id']
    volume_idx = parsed_features['volume_idx']
    label = parsed_features["label"]
    label_indicator = parsed_features["label_indicator"]

    return (volume,
            task_id,
            subject_id,
            run_id,
            volume_idx,
            label,
            label_indicator)