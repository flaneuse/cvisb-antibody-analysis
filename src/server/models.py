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
        return '<id {}>'.format(self.id)
