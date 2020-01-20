#!/usr/bin/python
import os
import pandas as pd
import numpy as np


def _generate_ev_df(path, ev_filenames, task, subject, run):
    df_list = []
    for f in ev_filenames:

        if task == 'GAMBLING':
            if 'win.txt' in f:
                continue
            elif 'loss.txt' in f:
                continue
            elif 'neut.txt' in f:
                continue
            else:
                if '_event' in f:
                    event_type = f.split('_')[-2].split('-')[1]
                else:
                    event_type = f.split('.')[-2].split('-')[1]
                ev_mat = pd.read_table(path+f, sep='\t', header=None).values
                df_tmp = pd.DataFrame({'subject': subject,
                                       'task': task,
                                       'run': run,
                                       'event_type': event_type,
                                       'onset': ev_mat[:, 0],
                                       'duration': ev_mat[:, 1],
                                       'end': ev_mat[:, 0] + ev_mat[:, 1]})

        elif task in ['EMOTION',
                      'LANGUAGE',
                      'MOTOR',
                      'RELATIONAL']:
            event_type = f.split('.')[0].split('_')[-1].split('-')[1]
            if (task == 'MOTOR') & (event_type == 'cue'):
                continue
            ev_mat = pd.read_table(path+f, sep='\t', header=None).values
            df_tmp = pd.DataFrame({'subject': subject,
                                   'task': task,
                                   'run': run,
                                   'event_type': event_type,
                                   'onset': ev_mat[:, 0],
                                   'duration': ev_mat[:, 1],
                                   'end': ev_mat[:, 0] + ev_mat[:, 1]})

        elif task == 'SOCIAL':
            if '_resp' in f:
                event_type = f.split('.')[0].split('_')[-2].split('-')[1]
                try:
                    ev_mat = pd.read_table(
                        path+f, sep='\t', header=None).values
                except pd.errors.EmptyDataError:
                    continue
                df_tmp = pd.DataFrame({'subject': subject,
                                       'task': task,
                                       'run': run,
                                       'event_type': event_type,
                                       'onset': ev_mat[:, 0],
                                       'duration': ev_mat[:, 1],
                                       'end': ev_mat[:, 0] + ev_mat[:, 1]})
            else:
                continue

        elif task == 'WM':
            event_type = f.split('.')[0].split('-')[-1].split('_')[1]
            if event_type in ['body', 'faces', 'places', 'tools']:
                ev_mat = pd.read_table(path+f, sep='\t', header=None).values
                df_tmp = pd.DataFrame({'subject': subject,
                                       'task': task,
                                       'run': run,
                                       'event_type': event_type,
                                       'onset': ev_mat[:, 0],
                                       'duration': ev_mat[:, 1],
                                       'end': ev_mat[:, 0] + ev_mat[:, 1]})
            else:
                continue

        else:
            raise NameError('Invalid task type.')
            break

        df_list.append(df_tmp)
    df = pd.concat(df_list)
    return df


def summarize_subject_EVs(task, subject, runs, path):
    df_list = []
    for run in runs:
        EV_files = [f for f in os.listdir(path) if
                    ('EV-' in f) and (task in f) and
                    ('run-{}'.format(run) in f) and not 'summary' in f]
        df_tmp = generate_ev_df(path, EV_files, task, subject, run)
        df_list.append(df_tmp)
    EV_summary = pd.concat(df_list)
    EV_summary = EV_summary.sort_values(by=['run', 'onset'])
    EV_summary['trial'] = np.arange(EV_summary.shape[0])
    return EV_summary.copy().reset_index(drop=True)