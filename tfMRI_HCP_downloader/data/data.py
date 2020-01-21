#!/usr/bin/python
import os
import pandas as pd
import numpy as np

from ._utils import _load_subject_data, _generate_ev_df


def summarize_subject_EVs(task, subject, runs, path):
    df_list = []
    for run in runs:
        EV_files = [f for f in os.listdir(path) if
                    ('EV-' in f) and (task in f) and
                    ('run-{}'.format(run) in f) and not 'summary' in f]
        df_tmp = _generate_ev_df(path, EV_files, task, subject, run)
        df_list.append(df_tmp)
    EV_summary = pd.concat(df_list)
    EV_summary = EV_summary.sort_values(by=['run', 'onset'])
    EV_summary['trial'] = np.arange(EV_summary.shape[0])
    return EV_summary.copy().reset_index(drop=True)


def load_subject_data(task, subject, run, path, TR):
    subject_data_dict = _load_subject_data(subject, task, [run], path, TR)
    return subject_data_dict
