"""empty message

Revision ID: 8548d72b8b9a
Revises: 8db0787fc047
Create Date: 2018-05-17 12:22:23.951191

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8548d72b8b9a'
down_revision = '8db0787fc047'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('file_upload',
    sa.Column('file_id', sa.Integer(), nullable=False),
    sa.Column('file', sa.LargeBinary(), nullable=True),
    sa.Column('file_type', sa.String(), nullable=True),
    sa.Column('expt_id', sa.String(), nullable=True),
    sa.Column('expt_type', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('file_id')
    )
    op.drop_table('file_uploads')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('file_uploads',
    sa.Column('file_id', sa.INTEGER(), nullable=False),
    sa.Column('file', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('file_type', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('expt_id', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('expt_type', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('file_id', name='file_uploads_pkey')
    )
    op.drop_table('file_upload')
    # ### end Alembic commands ###
