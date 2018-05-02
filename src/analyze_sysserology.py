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

# [0] Define the locations of the files -------------------------------------------------------------------
wd = '/Users/laurahughes/GitHub/cvisb-antibody-analysis/example_data/'

# lookup table containing the sample ids + locations on the plate
platefile = '/Users/laurahughes/GitHub/cvisb-antibody-analysis/example_data/ADNP_PlateLayout.xlsx'

# Export from FlowJo containing the processed fluorescence counts
fluorfile = '/Users/laurahughes/GitHub/cvisb-antibody-analysis/example_data/ADNP_data from FlowJo.xlsx'

# zipped file from FlowJo containing the raw data files + gating info + metadata
fcsfile = 'ADNP_Tulane.acs'

# [1] Read in the plate metadata file ---------------------------------------------------------------------
plate_dict, expt_ids = read_plates(platefile)

# [2] Create dirs + logfile -------------------------------------------------------------------------------
# Returns a dict containing all the necessary paths for the experiment
expt_dict = create_dirs(expt_ids, wd)

expt_dict

# [3] Pull out metadata and rename files ------------------------------------------------------------------
