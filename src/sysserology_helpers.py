# @name:        sysserology_helpers.py
# @summary:
# @description:
# @sources:
# @depends:
# @author:      Laura Hughes
# @email:       lhughes@scripps.edu
# @license:     Apache-2.0
# @date:        25 April 2018

import pandas as pd
import os

# --- setup ---

# [Define output directories] ---------------------------------------------------------------------------
# looped version: will go through all
def create_dirs(expt_ids, exptdir):
    expt_dict = dict()
    for expt_id, expt_type in expt_ids.items():
        inputdir, datadir, gatingdir, tmpdir, metadir, logfile = create_dirs_1expt(expt_id, expt_type, exptdir)
        expt_dict[expt_id] = {
        'type': expt_type, 'logfile': logfile,
        'exptdir': exptdir, 'inputdir': inputdir,
        'datadir': datadir, 'gatingdir': gatingdir,
        'tmpdir': tmpdir, 'metadir': metadir
        }

    return(expt_dict)

def create_dirs_1expt(expt_id, expt_type, exptdir):
    # TODO: check if exptdir ends in a '/'; if not, append
    inputdir = f'{exptdir}{expt_id}/input'

    datadir = f'{inputdir}/fcs'

    gatingdir = f'{inputdir}/gating'

    # temp for unzipping files
    tmpdir = f'{exptdir}{expt_id}/tmp/'

    metadir = f'{exptdir}{expt_id}/metadata/'

    logdir = f'{exptdir}{expt_id}/log/'

    # create output directories
    # create logfile + logdir
    try:
        os.makedirs(logdir)
        logfile = Logfile(logdir, expt_id, expt_type)
        logfile.section("Creating directories for files")

    except:
        logfile = Logfile(logdir, expt_id, expt_type)
        logfile.section("Creating directories for files")
        logfile.write(f"{logdir} already exists -- no need to create")



    # directory for storing input data -- exports from FlowJo + raw fcs files
    try:
        os.makedirs(datadir)
    except:
        logfile.write(f"{datadir} already exists -- no need to create")

    # directory for storing gating data
    try:
        os.makedirs(gatingdir)
    except:
        logfile.write(f"{gatingdir} already exists -- no need to create")

    # temp directory for storing gating dat
    try:
        os.makedirs(gatingdir)
    except:
        logfile.write(f"{gatingdir} already exists -- no need to create")


    # directory for storing metadata
    try:
        os.makedirs(metadir)
    except:
        logfile.write(f"{metadir} already exists -- no need to create")

    logfile.endsection("done creating directories")

    return([inputdir, datadir, gatingdir, tmpdir, metadir, logfile])

class Logfile:
    def __init__(self, logdir, expt_id, expt_type, logfile = 'logfile.txt'):
        self.logdir = logdir
        self.expt_id = expt_id
        self.expt_type = expt_type
        self.logfile = f'{logdir}{expt_type}_{expt_id}_{logfile}'
        self.create()

    def create(self):
        print('creating logfile')

        with open(f'{self.logfile}', 'w') as mylog:
            mylog.write(f"LOGFILE FOR {self.expt_type.upper()} EXPERIMENT {self.expt_id.upper()}:\n\n")

    def write(self, msg):
        print(msg)
        with open(f'{self.logfile}', 'a') as mylog:
            mylog.write(msg + "\n")

    def section(self, section_header):
        msg = f"-- {section_header} --"
        self.write(msg)

    def endsection(self, section_end):
        msg = f"----- {section_end}!\n"
        self.write(msg)



# [Lookup table for the plate geometry, to map samples to wells] ----------------------------------------
def read_plates(platefile):
    meta_cols = ['plate', 'well', 'sample_id', 'sample_type',
               'experiment', 'sample_dilution', 'cell_donor', 'expt_id']
    plate_dict = pd.read_excel(platefile, sheetname=None)

    # combined across all plates
    plates = pd.DataFrame()

    # combine all the plates together
    for name, plate in plate_dict.items():
        if(name != 'lookup tables'):
            # pull out the actual plate geometry
            try:
                plates = plates.append(plate[meta_cols], ignore_index=True)
            except:
                msg = f"Sheet '{name}' in {platefile} is missing 1+ columns of {meta_cols}. Rename the plate template columns to match."
                write_logfile(msg)

    # pull out the experimental id for the given experiment
    # expt_ids = dict of
    expt_ids = dict(zip(plates.expt_id, plates.experiment))

    return(plates, expt_ids)
