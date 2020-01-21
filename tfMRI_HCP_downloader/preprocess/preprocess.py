#!/usr/bin/python
import numpy as np

from .data import _load_subject_data

import nilearn as nl


def _clean_func(func, mask, smoothing_fwhm=3, high_pass=1./128., tr=0.72):
    masked_func = nl.maksing.apply_mask(func,
                                        mask,
                                        smoothing_fwhm=smoothing_fwhm,
                                        ensure_finite=True)
    masked_func = nl.signal.clean(masked_func,
                                  detrend=True,
                                  standardize=True,
                                  high_pass=high_pass,
                                  t_r=tr,
                                  ensure_finite=True)
    unmasked_func = nl.maksing.unmask(masked_func, mask)
    return unmasked_func


def preprocess_subject_data(subject_data, runs, high_pass. smoothing_fwhm):

    func = []
    volume_label = []
    for run in runs:
        # load tfMRI data
        func_run = nl.image.load_img(subject_data[run]['func_mni'])
        mask_run = nl.image.load_img(subject_data[run]['func_mask_mni'])

        trial_type = subject_data[run]['trial_type']
        cleaned_func = _clean_func(func_run, mask_run, smoothing_fwhm=smoothing_fwhm, high_pass=high_pass, tr=subject_data['tr'])

        # subset tfMRI data to valid volumes
        valid_volume_idx = np.isfinite(trial_type)
        valid_func = nl.image.index_img(cleaned_func, valid_volume_idx)
        valid_trial_type = trial_type[valid_volume_idx]

        func.append(valid_func)
        volume_label.append(valid_trial_type)

    volume_label = np.concat(volume_label)
    func = nl.image.concat_imgs(func)

    return func, volume_label
