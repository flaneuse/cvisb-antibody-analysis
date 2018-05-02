# @name:        metadata.py
# @summary:     pulls metadata from an FCS experiment
# @description:
# @sources:
# @depends:
# @author:      Laura Hughes
# @email:       lhughes@scripps.edu
# @license:     Apache-2.0
# @date:        23 April 2018

# [Import dependencies] ---------------------------------------------------------------------------------
# --- data manipulation ---
import pandas as pd
import re  # regular expression / string matching

# --- file manipulation ---
import os
import zipfile

# --- flow cytometry ---
import FlowCytometryTools
from FlowCytometryTools import FCMeasurement

# --- common helper functions ---
# TODO: fix paths
os.chdir('/Users/laurahughes/GitHub/cvisb-antibody-analysis/src')
# from sysserology_helpers import write_logfile, read_plates


wd = '/Users/laurahughes/GitHub/cvisb-antibody-analysis/example_data/'
os.chdir(wd)
# def get_metadata():

# [setup] -----------------------------------------------------------------------------------------------
# --- inputs ---
# TODO: common input file
# template to match well locations to unique sample IDs
platefile = 'ADNP_PlateLayout.xlsx'

# zipped file from FlowJo containing the raw data files + gating info + metadata
fcsfile = 'ADNP_Tulane.acs'


# TODO: try/catch no data


def unzip_acs(fcsfile, tmpdir):
    # [Unzip the FlowJo .acs file to individual .fcs files] -------------------------------------------------
    acs_ref = zipfile.ZipFile(fcsfile, 'r')
    acs_ref.extractall(tmpdir)
    acs_ref.close()


def find_files(fcs_filelist, plate_num, well, logfile):
    fcs_string = f"{plate_num}\.\w+{well}\_.+\.fcs"
    gate_string = f"{plate_num}\_\w+{well}\_.+\.xml"

    datafile = find_file(fcs_filelist, fcs_string)
    gatefile = find_file(fcs_filelist, gate_string)
    # matched_files = filter(r.match, fcs_filelist)  # returns iterator
    # list(matched_files)

    if(len(datafile) == 0):
        logfile.write(
            f"Missing .fcs data file for well {well}, plate {plate_num}")

    if(len(gatefile) == 0):
        logfile.write(
            f"Missing .xml gating file for well {well}, plate {plate_num}")

    return({'datafile': datafile, 'gatefile': gatefile})


def find_file(filelist, search_string, exact_match=False):
    if(not exact_match):
        search_string = ".*" + search_string + ".*"

    search = re.compile(search_string)
    file = [x for x in filelist if search.match(x)]

    # if there's only one match, convert from array to string
    if (len(file) == 1):
        return file[0]
    return file

# [Move and rename the .fcs files] ----------------------------------------------------------------------


def rename_fcs(fcs_filelist, sample, md, datadir, gatingdir, tmpdir, logfile):
    well = sample.well
    plate_num = sample.plate

    result = find_files(fcs_filelist, plate_num, well, logfile)
    datafile = result['datafile']
    gatefile = result['gatefile']

    # [Pull out the metadata] -------------------------------------------------------------------------------
    # Read in FCS data to get the metadata
# TODO: check if datafile has > 1 arg.
    if len(datafile) == 0:
        # error should have already been recorded in the 'find_files' function
        print("datafile is empty")
    else:
        fcs_data = FCMeasurement(ID=well, datafile=tmpdir + datafile, readdata=False)
        fcs_date = pd.to_datetime(fcs_data.meta['$DATE'])
        fcs_date = fcs_date.strftime("%Y-%m-%d")

        # Create filenames
        fcs_filename = f'{sample.sample_id}-plate{plate_num}-{well}_sysserology-{sample.expt_id}_{fcs_date}.fcs'
        gate_filename = f'{sample.sample_id}-plate{plate_num}-{well}_sysserology-{sample.expt_id}_{fcs_date}_gates.xml'

        md = get_metadata(sample, fcs_data, fcs_date, fcs_filename, md)

        # [Rename the data files] -------------------------------------------------------------------------------
        os.rename(tmpdir + datafile, f'{datadir}/{fcs_filename}')

    try:
        os.rename(tmpdir + gatefile, f'{gatingdir}/{gate_filename}')
    except:
        # error should have already been recorded in the 'find_files' function; no need to log again
        pass
    return md


def get_metadata(sample, fcs_data, fcs_date, fcs_filename, md):
    # Here's where it's defined which automatically saved info to pull from the fcs files.
    md = md.append({
        'sample_id': sample.sample_id,
        'plate': sample.plate,
        'well': sample.well,
        'original_file': fcs_data.meta['$FIL'],
        'renamed_file': fcs_filename,
        'expt_name': fcs_data.meta['EXPERIMENT NAME'],
        'sample_name': fcs_data.meta['$SRC'],
        'plate name': fcs_data.meta['PLATE NAME'],
        'sample_date': fcs_date,
        'flow_cytometer': fcs_data.meta['$CYT'],
        'fcs_version': fcs_data.meta['CREATOR'],
        'fcs_settings': fcs_data.meta['SETTINGS'],
        'username': fcs_data.meta['EXPORT USER NAME']
    }, ignore_index=True)
    return md


def getmd_renamefiles(plates, expt_dict):
    for expt_id, expt_dirs  in expt_dict.items():
        print(expt_id)
        # only grab the portion of the plate lookup table containing current expt
        filtered_plates = plates[plates.expt_id == expt_id]

        getmd_renamefiles_1expt(filtered_plates, expt_id, expt_dirs)


def getmd_renamefiles_1expt(plates, expt_id, expt_dirs):
    # metadata holder
    md = pd.DataFrame()

    # grab the output directories
    datadir = expt_dirs['datadir']
    gatingdir = expt_dirs['gatingdir']
    tmpdir = expt_dirs['tmpdir']
    metadir = expt_dirs['metadir']
    logfile = expt_dirs['logfile']
    expt_type = expt_dirs['type']

    print(logfile.logfile)

    # unzip the .fcs files
    unzip_acs(fcsfile, tmpdir)

    # TODO: copy the FlowJo XLSX files

    # rename the .fcs files, pull out metadata
    logfile.section("RENAMING FCS & GATING FILES")
    fcs_filelist = os.listdir(tmpdir)

    for idx, row in plates.iterrows():
        md = rename_fcs(fcs_filelist, row, md, datadir, gatingdir, tmpdir, logfile)

    md = pd.merge(plates, md, on=['plate', 'well', 'sample_id'])
    # export to .csv file
    md.to_csv(metadir + f"{expt_type}-{expt_id}_metadata.csv", sep=',')
    logfile.endsection('.fcs/gating files renamed, metadata extracted')

    # remove temp directory
    rm_tmp(tmpdir, logfile)

def rm_tmp(tmpdir, logfile):
    # refresh the files in the working directory:
    fcs_filelist = os.listdir(tmpdir)
    # Remove the two extra files that always come along for the ride
    # FlowJo workspace file
    workspace_file = find_file(fcs_filelist, "\.wsp")
    os.remove(tmpdir + workspace_file)

    # FlowJo table of contents xml file, which seems worthless
    toc_file = find_file(fcs_filelist, "ToC.xml")
    os.remove(tmpdir + toc_file)

    try:
        os.rmdir(tmpdir)
    except:
        logfile.write(
            f"Warning: not all .fcs data files were processed. This often happens if you have two experimental IDs in the same .acs file. {os.listdir(tmpdir)} files remain")


# x = process_files(platefile)
