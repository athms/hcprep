#!/usr/bin/python
import os
import pandas as pd
import numpy as np

from ._utils import _load_subject_data, _generate_ev_df


def summarize_subject_EVs(task, subject, runs, path):
    """Summarize EV data of a task and subject, across runs.

    Args:
        task: String of HCP task name
        subject: Integer HCP subject ID
        runs: A sequence of the runs ["LR", "RL"] for 
            which to summarize the EV data.
        path: Path to the local HCP data in BIDS format.

    Returns:
        EV_summary: Pandas dataframe summarizing the EV data.
    """
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


def load_subject_data(task, subject, runs, path, TR=0.72):
    """Return a dict summarizing the data of a
    subject in a run of a task.

    Args:
        task: String of HCP task name
        subject: Integer HCP subject ID
        runs: A sequence of the runs ["LR", "RL"] for 
            which to summarize the EV data.
        path: Path to the local HCP data in BIDS format.
        TR: Repetition time of HCP data

    Returns:
        Dict of data, containing one entry per run and
            a summary of the fMRI data for this run
            (incl. the paths for the fMRI data files).
    """
    subject_data_dict = _load_subject_data(subject, task, runs, path, TR)
    return subject_data_dict
