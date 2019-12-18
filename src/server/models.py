from server.server import db
from werkzeug.datastructures import FileStorage
from sqlalchemy.dialects.postgresql import JSON


class FileRef(db.Model):
    __tablename__ = 'file_upload'

    file_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    file = db.Column(db.LargeBinary)
    file_type = db.Column(db.String())
    expt_id = db.Column(db.String())
    expt_type = db.Column(db.String())

    def __init__(self, file, file_type, expt_id, expt_type):
        self.file = file
        self.file_type = file_type
        self.expt_id = expt_id
        self.expt_type = expt_type

    def __repr__(self):
        return '<file id {}>'.format(self.file_id)


class Plate(db.Model):
    __tablename__ = 'plate_dict'

    plate_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    plate = db.Column(db.Integer)
    well = db.Column(db.String())
    sample_id = db.Column(db.String())
    sample_type = db.Column(db.String())
    experiment = db.Column(db.String())
    sample_dilution = db.Column(db.String())
    cell_donor = db.Column(db.String())
    expt_id = db.Column(db.String())
    # expt_type = db.Column(db.String())

    def __init__(self, plate, well, sample_id, sample_type, experiment, sample_dilution, cell_donor, expt_id, expt_type):
        self.plate = plate
        self.well = well
        self.sample_id = sample_id
        self.sample_type = sample_type
        self.experiment = experiment
        self.sample_dilution = sample_dilution
        self.cell_donor = cell_donor
        self.expt_id = expt_id
        # self.expt_type = expt_type

    def __repr__(self):
        return '<plate id {}>'.format(self.plate_id)

    def serialize(self):
        return {
        'plate_id': self.plate_id,
        'well': self.well,
        'expt_id': self.expt_id
        }

class FluorTable(db.Model):
    __tablename__ = 'fluor'

    # id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    filename = db.Column(db.String())
    pct_fluor = db.Column(db.Float())
    MFI = db.Column(db.Float())
    plate = db.Column(db.Integer)
    well = db.Column(db.String(), primary_key=True)
    row = db.Column(db.String())
    col = db.Column(db.String())
    pct_fluor_source = db.Column(db.String())
    MFI_source = db.Column(db.String())

    db.relationship('Plate', backref='fluortable')

    def __init(self, filename, pct_fluor, MFI, plate, well, row, col, pct_fluor_source, MFI_source):
        self.filename = filename
        self.pct_fluor = pct_fluor
        self.MFI = MFI
        self.plate = plate
        self.well = well
        self.row = row
        self.col = col
        self.pct_fluor_source = pct_fluor_source
        self.MFI_source = MFI_source

    def __repr__(self):
        return '<obs id {}>'.format(self.MFI)

    def serialize(self):
        return {
        'MFI': self.MFI,
        'well': self.well
        }
