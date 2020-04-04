#!/usr/bin/python
import numpy as np


class basics:
    """A simple class containing
    all basic information about the 
    Human Connectome Project task-fMRI data.

    Attributes:
        tasks: task names
        classes_per_task: Dictionary of class names 
            per task
        n_classes_per_task: List with number of classes
            per task
        runs: List or run names
        subjects: Dictionary of subject IDs for each task
        t_r: Repetition time of fMRI data (in seconds)
    """

    def __init__(self):
        self.tasks = ['EMOTION',
                      'GAMBLING',
                      'LANGUAGE',
                      'MOTOR',
                      'RELATIONAL',
                      'SOCIAL',
                      'WM']
        self.classes_per_task = dict(EMOTION=['fear', 'neut'],
                                     GAMBLING=['loss', 'neut', 'win'],
                                     LANGUAGE=['math', 'story'],
                                     MOTOR=['lf', 'lh', 'rf', 'rh', 't'],
                                     RELATIONAL=['match', 'relation'],
                                     SOCIAL=['mental', 'other'],
                                     WM=['body', 'faces', 'places', 'tools'])
        self.n_classes_per_task = [len(self.classes_per_task[task])
                                   for task in self.tasks]
        self.runs = ['LR', 'RL']
        self.subjects = dict()
        for task in self.tasks:
            self.subjects[task] = np.load(
                'hcprep/info/subject_ids/task-{}_subjects.npy'.format(task))
        self.t_r = 0.72
