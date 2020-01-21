#!/usr/bin/python
import numpy as np
from nilearn.masking import apply_mask, unmask
from nilearn.signal import clean
from nilearn.image import load_img, index_img, concat_imgs

from ..data._utils import _load_subject_data


def _clean_func(func, mask, smoothing_fwhm=3, high_pass=1./128., tr=0.72):
    masked_func = apply_mask(func,
                             mask,
                             smoothing_fwhm=smoothing_fwhm,
                             ensure_finite=True)
    masked_func = clean(masked_func,
                        detrend=True,
                        standardize=True,
                        high_pass=high_pass,
                        t_r=tr,
                        ensure_finite=True)
    unmasked_func = unmask(masked_func, mask)
    return unmasked_func


def preprocess_subject_data(subject_data, runs, high_pass, smoothing_fwhm):

    func = []
    volume_label = []
    for run in runs:
        # load tfMRI data
        func_run = load_img(subject_data[run]['func_mni'])
        mask_run = load_img(subject_data[run]['func_mask_mni'])

        trial_type = subject_data[run]['trial_type']
        cleaned_func = _clean_func(
            func_run, mask_run, smoothing_fwhm=smoothing_fwhm, high_pass=high_pass, tr=subject_data['tr'])

        # subset tfMRI data to valid volumes
        valid_volume_idx = np.isfinite(trial_type)
        valid_func = index_img(cleaned_func, valid_volume_idx)
        valid_trial_type = trial_type[valid_volume_idx]

        func.append(valid_func)
        volume_label.append(valid_trial_type)

    volume_label = np.concatenate(volume_label)
    func = concat_imgs(func)

    return func, volume_label
