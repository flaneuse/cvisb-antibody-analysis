# @name:        adcd.py
# @summary:     Calculations for ADCD experiment
# @description: Imports fluorescence data from flow cytometry antibody-dependent complement detection
# @sources:
# @depends:     pandas, numpy, scipy
# @author:      Laura Hughes
# @email:       lhughes@scripps.edu
# @license:     Apache-2.0
# @date:        17 April 2018

import pandas as pd
import numpy as np
import os

from scipy.stats import percentileofscore
# os.chdir('/Users/laurahughes/GitHub/cvisb-antibody-analysis/src/calculations')
from calculations.SysSerologyExpt import SysSerologyExpt


# [Calculate ratios + average values] -------------------------------------------------------------------
# NOTE: this is where you adjust the calculations
class ADCD(SysSerologyExpt):
    # !!!! [1/3] !!!! Adjust the columns within the Excel sheet
    # define which columns used in the calculations
    # format: {'column name in FlowJo spreadsheet': 'what to rename it to'}
    fluor_cols = {
    'beads/PerCP-Cy5-5-A, SSC-A subset | Geometric Mean (FITC-A)': 'MFI_all',
       'beads/PerCP-Cy5-5-A, SSC-A subset/FITC-A subset | Freq. of Parent': 'pct_fluor',
       'beads/PerCP-Cy5-5-A, SSC-A subset/FITC-A subset | Geometric Mean (FITC-A)': 'MFI'
       }

    def calc_score(self):
        # !!!! [2/3] CALCULATION DEFINITION !!!! Change as needed
        # Creates a new column called 'fluor_score' which calculates the fluorescence score
        self.df['fluor_score'] = self.df.MFI * self.df.pct_fluor / self.scale_factor
        self.df['fluor_score_type'] = 'phagocytotic score'

        self.run_qc()

        return self.df

# !!!! [3/3] Change QC !!!!
    def run_qc(self):
        """
        Function used to run some basic quality control on the fluorescence scores
        """
        self.df['fluor_percentile'] = self.df.fluor_score.apply(lambda x: percentileofscore(self.df.fluor_score, x))

    def __init__(self, fluorfile, platefile, expt_dict):
        super().__init__(fluorfile, platefile, expt_dict)



# np.trapz(np.array([22.7493,	17.768735,	13.9848]), np.array([150, 750, 3750])) / np.trapz(np.array([86.765295,	94.033755,	25.95186]), np.array([150, 750, 3750]))
#
# np.trapz(np.array([13.9848, 17.768735,	22.7493]), np.log10([1/3750, 1/750, 1/150])) / np.trapz(np.array([25.95186, 94.033755,	86.765295]), np.log10([1/3750, 1/750, 1/150]))
#
# np.trapz(np.array([13.9848, 17.768735,	22.7493]), np.array([1/3750, 1/750, 1/150])) / np.trapz(np.array([25.95186, 94.033755,	86.765295]), np.array([1/3750, 1/750, 1/150]))
