# @name:        analyze_sysserology.py
# @summary:
# @description:
# @sources:
# @depends:
# @author:      Laura Hughes
# @email:       lhughes@scripps.edu
# @license:     Apache-2.0
# @date:        2 May 2018


# [0] Import the dependent functions ----------------------------------------------------------------------
import os

os.chdir('/Users/laurahughes/GitHub/cvisb-antibody-analysis/src')
from sysserology_helpers import read_plates, create_dirs
from metadata import getmd_renamefiles, unzip_acs

# TODO: relative paths
# TODO: figure more convenient place for these
# [0] Define the locations of the files -------------------------------------------------------------------
wd = '/Users/laurahughes/GitHub/cvisb-antibody-analysis/example_data/'

# lookup table containing the sample ids + locations on the plate
platefile = '/Users/laurahughes/GitHub/cvisb-antibody-analysis/example_data/ADNP_PlateLayout.xlsx'

# Export from FlowJo containing the processed fluorescence counts
fluorfile = '/Users/laurahughes/GitHub/cvisb-antibody-analysis/example_data/ADNP_data from FlowJo.xlsx'

# zipped file from FlowJo containing the raw data files + gating info + metadata
fcsfile = '/Users/laurahughes/GitHub/cvisb-antibody-analysis/example_data/ADNP_Tulane.acs'

# [1] Read in the plate metadata file ---------------------------------------------------------------------
plates, expt_ids = read_plates(platefile)

# [2] Create dirs + logfile -------------------------------------------------------------------------------
# Returns a dict containing all the necessary paths for the experiment
expt_dict = create_dirs(expt_ids, wd)

# expt_dict['BMGEXP568']

# [3] Pull out metadata and rename files ------------------------------------------------------------------
getmd_renamefiles(plates, expt_dict, fcsfile, platefile, fluorfile)

for expt_id, expt_dirs  in expt_dict.items():
    print(expt_id)
    print(expt_dirs)

# [4] Call experiment calculation ------------------------------------------------------------------------
expt = ADNP(fluor_vals)
