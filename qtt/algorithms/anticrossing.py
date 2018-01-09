""" Functions to fit anticrossings in charge stability diagrams. """

#%% import modules
import copy
import numpy as np
import matplotlib.pyplot as plt

import qtt
from qtt.legacy import fixReversal, cleanSensingImage, straightenImage
from qtt.deprecated.linetools import evaluateCross, Vtrace, fitModel

#%%
def fit_anticrossing(dataset, width_guess=None, angles_guess=None, psi=None, w=2.5, diff_dir='dx', plot=False, verbose=1):
    """ Fits an anti-crossing model to a 2D scan
    
    Args:
        dataset (qcodes dataset): the 2D scan measurement dataset
        width_guess (float): initial guess for the length of the polarization line
        angles_guess (list): list of 4 elements, initial guess of the angles of the ' arms' of the model
        psi (float): initial guess for the angle of the polarization line
        w (float): initial guess for the width of the polarization line
        diff_dir (str): direction of derivative with is taken of the dataset, options: 'dx' ,'dy', 'dxy' and 'xmy'
        plot (bool): when true plots the dataset with the fit superimposed
        verbose (int): determines the amount of information returned
        
    Returns:
        anticross_fit: (dict) the parameters describing the fitted anti-cross
                       optionally the cost for fitting and the figure number
    """
    abs_val = True
    im, tr = qtt.data.dataset2image(dataset, arrayname='measured')
    imextent = tr.scan_image_extent()
    istep = .25

    diffvals = {'dx': 0, 'dy': 1, 'dxy': 2, 'xmy': 'xmy'}
    imc = cleanSensingImage(im, sigma=0.93, dy=diffvals[diff_dir])
    imx, (fw, fh, mvx, mvy, Hstraight) = straightenImage(
        imc, imextent, mvx=istep, verbose=verbose)

    imx = imx.astype(np.float64) * \
        (100. / np.percentile(imx, 99))  # scale image

    # initialization of anti-crossing model
    istepmodel = .5
    ksizemv = 31
    param0 = [(imx.shape[0] / 2 + .5) * istep, (imx.shape[0] / 2 + .5) * istep, \
          3.5, 1.17809725, 3.5, 4.3196899, 0.39269908]

    if width_guess is not None:
        param0[2] = width_guess
    
    if angles_guess is not None:
        param0[3:] = angles_guess

    if psi is not None:
        param0e = np.hstack((param0, [psi]))
    else:
        psi = np.pi / 4
        param0e = copy.copy(param0)

    # fit anti-crossing (twice)
    res = fitModel(param0e, imx, verbose=verbose, cfig=10, istep=istep,
                   istepmodel=istepmodel, ksizemv=ksizemv, w=w, use_abs=abs_val)
    param = res.x
    res = fitModel(param, imx, verbose=verbose, cfig=10, istep=istep,
                   istepmodel=istepmodel, ksizemv=ksizemv, w=w, use_abs=abs_val)
    param = res.x

    anticross_fit = {}
    if plot:
        fig_anticross = plt.figure()
        cost, patch, cdata, _ = evaluateCross(
            param, imx, verbose=verbose, fig=fig_anticross.number, istep=istep, istepmodel=istepmodel, w=w)
        anticross_fit['cost'] = cost
        anticross_fit['patch'] = patch
        anticross_fit['cdata'] = cdata
        anticross_fit['fig_num'] = fig_anticross.number
        anticross_fit['imx'] = imx

    if len(param) == 7:
        param = np.append(param, psi)
    anticross_fit['fit_params'] = param

    return anticross_fit

#%%



