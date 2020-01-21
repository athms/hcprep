#!/usr/bin/python
import os
import pandas as pd
import numpy as np

import nilearn as nl

from .. import paths 


def _init_datadict(subject,
		            task,
		            runs,
		            path,
		            n_classes,
		            TR):
    f = {}
    f['anat'] = None
    f['anat_mni'] = None
    f['tr'] = TR
    f['runs'] = runs
    for ri, run in enumerate(runs):
        f_run = {}
        f_run['func'] = None
        f_run['func_mni'] = paths.path_bids_func_mni(subject, task, run, path)
        f_run['func_mask_mni'] = paths.path_bids_func_mask_mni(subject, task, run, path)
        f_run['n_volumes'] = np.int(nl.load_img(f_run['func_mni']).shape[-1])
        f_run['trial'] = np.zeros(f_run['n_volumes']) * np.nan
        f_run['n_trial_volumes'] = np.zeros_like(f_run['trial']) * np.nan
        f_run['rel_onset'] = np.zeros_like(f_run['trial']) * np.nan
        f_run['trial_type'] = np.zeros_like(f_run['trial']) * np.nan
        f_run['n_valid_volumes'] = 0
        f_run['n_trials'] = 0
        f_run['onset'] = np.arange(0, f_run['n_volumes']*TR, TR)
        f_run['end'] = f_run['onset'] + TR

        f[run] = f_run
    return f


def _add_markers_to_datadict(f, EV, n_volumes_discard_trial_onset=1, n_volumes_add_trial_end=1):

    # extract TR
    TR = f['tr']

    # recode stimulus classes
    event_types = EV['event_type'].values
    unique_event_types = np.sort(np.unique(event_types))
    numerical_event_types = np.arange(unique_event_types.size)
    mapping = {}
    f['event_type_mapping'] = {}
    for num_type in numerical_event_types:
        f['event_type_mapping'][num_type] = unique_event_types[num_type]
    f['event_type_mapping'][numerical_event_types.max()+1] = 'fixation'
    tmp = np.ones_like(event_types) * np.nan
    for event_type in unique_event_types:
        tmp[np.where(event_types == event_type)[0]] = numerical_event_types[
            np.where(unique_event_types == event_type)[0]]
    EV['event_num'] = np.array(tmp)

    # insert marker data
    runs = EV['run'].unique()
    for run in runs:
        run_data = EV[EV['run'] == run].copy()
        trials = np.sort(run_data['trial'].values)
        for trial in trials:
            trial_data = run_data[run_data['trial'] == trial].copy()

            trial_type = trial_data['event_num'].values[0]
            run = trial_data['run'].values[0]
            trial_onset = trial_data['onset'].values[0]
            trial_end = trial_data['end'].values[0]
            volume_idx = np.where((f[run]['onset'] >= (trial_onset +
                                                       (n_volumes_discard_trial_onset*TR))) &
                                  (f[run]['onset'] <= (trial_end+TR +
                                                       (n_volumes_add_trial_end*TR))))[0]
            f[run]['trial'][volume_idx] = trial
            f[run]['n_trial_volumes'][volume_idx] = volume_idx.size
            f[run]['rel_onset'][volume_idx] = f[run]['onset'][volume_idx] - trial_onset
            f[run]['trial_type'][volume_idx] = trial_type
            f[run]['n_valid_volumes'] += len(volume_idx)
            f[run]['n_trials'] += 1

    return f


def _load_subject_data(subject, task, runs, path, TR):
    F_init = _init_datadict(subject, task, runs, path)
    EV_list = []
    for run in runs:
        EV_run = pd.read_csv(path_bids_EV(subject, task, run, path))
        EV_list.append(EV_run)
    F = _add_markers_to_datadict(f_init, pd.concat(EV_list))
    return F