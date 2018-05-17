import pandas as pd
import os

import re

from scipy.stats import percentileofscore



def calc_score(expt_type):
    if(expt_type == 'ADCD'):
        return adcd_score()
    elif(expt_type == 'ADCP'):
        return adcp_score()
    elif(expt_type == 'ADNP'):
        return adnp_score()
    elif(expt_type == 'NKD'):
        return nkd_score()
    else:
        write_logfile(f"unrecognized experiment type {expt_type}")
        pass

platefile = '/Users/laurahughes/GitHub/cvisb-antibody-analysis/example_data/ADNP_PlateLayout.xlsx'
plates = read_plates(platefile)
plates
# [Merge together cell w/ sample ID] --------------------------------------------------------------------
