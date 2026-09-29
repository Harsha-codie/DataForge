"""initial dataforge schema

Revision ID: 001_initial_dataforge_schema
Revises: 
Create Date: 2026-09-25 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001_initial_dataforge_schema'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # Datasets table
    op.create_table(
        'datasets',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('original_filename', sa.String(255), nullable=False),
        sa.Column('format', sa.String(32), nullable=False),
        sa.Column('file_size_bytes', sa.BigInteger(), nullable=False, default=0),
        sa.Column('current_version_id', sa.String(36), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_datasets_user_id', 'datasets', ['user_id'])

    # Dataset Versions table
    op.create_table(
        'dataset_versions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('dataset_id', sa.String(36), sa.ForeignKey('datasets.id', ondelete='CASCADE'), nullable=False),
        sa.Column('version_number', sa.Integer(), nullable=False),
        sa.Column('branch_name', sa.String(64), nullable=False, default='main'),
        sa.Column('parent_version_id', sa.String(36), sa.ForeignKey('dataset_versions.id', ondelete='SET NULL'), nullable=True),
        sa.Column('storage_path', sa.String(512), nullable=False),
        sa.Column('file_checksum', sa.String(64), nullable=True),
        sa.Column('file_format', sa.String(32), nullable=False, default='parquet'),
        sa.Column('row_count', sa.Integer(), nullable=False, default=0),
        sa.Column('column_count', sa.Integer(), nullable=False, default=0),
        sa.Column('schema_metadata', sa.JSON(), nullable=True),
        sa.Column('transformation_operation', sa.String(128), nullable=False, default='upload'),
        sa.Column('transformation_params', sa.JSON(), nullable=True),
        sa.Column('execution_status', sa.String(32), nullable=False, default='ready'),
        sa.Column('created_by_user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_dataset_versions_dataset_id', 'dataset_versions', ['dataset_id'])

    # Dataset Schemas table
    op.create_table(
        'dataset_schemas',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('dataset_id', sa.String(36), sa.ForeignKey('datasets.id', ondelete='CASCADE'), nullable=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('schema_definition', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_dataset_schemas_user_id', 'dataset_schemas', ['user_id'])
    op.create_index('ix_dataset_schemas_dataset_id', 'dataset_schemas', ['dataset_id'])

    # Transformation Runs table
    op.create_table(
        'transformation_runs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('dataset_id', sa.String(36), sa.ForeignKey('datasets.id', ondelete='CASCADE'), nullable=False),
        sa.Column('source_version_id', sa.String(36), sa.ForeignKey('dataset_versions.id', ondelete='SET NULL'), nullable=True),
        sa.Column('target_version_id', sa.String(36), sa.ForeignKey('dataset_versions.id', ondelete='SET NULL'), nullable=True),
        sa.Column('operation', sa.String(128), nullable=False),
        sa.Column('parameters', sa.JSON(), nullable=False),
        sa.Column('status', sa.String(32), nullable=False, default='completed'),
        sa.Column('summary', sa.JSON(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('executed_by_user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_transformation_runs_dataset_id', 'transformation_runs', ['dataset_id'])

    # Validation Reports table
    op.create_table(
        'validation_reports',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('dataset_id', sa.String(36), sa.ForeignKey('datasets.id', ondelete='CASCADE'), nullable=False),
        sa.Column('version_id', sa.String(36), sa.ForeignKey('dataset_versions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('overall_status', sa.String(32), nullable=False),
        sa.Column('rules_checked', sa.JSON(), nullable=False),
        sa.Column('violations_count', sa.Integer(), nullable=False, default=0),
        sa.Column('issues', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_validation_reports_dataset_id', 'validation_reports', ['dataset_id'])
    op.create_index('ix_validation_reports_version_id', 'validation_reports', ['version_id'])

    # Background Jobs table
    op.create_table(
        'background_jobs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('dataset_id', sa.String(36), sa.ForeignKey('datasets.id', ondelete='CASCADE'), nullable=True),
        sa.Column('job_type', sa.String(64), nullable=False),
        sa.Column('status', sa.String(32), nullable=False, default='queued'),
        sa.Column('progress_percent', sa.Integer(), nullable=False, default=0),
        sa.Column('message', sa.String(255), nullable=True),
        sa.Column('result_payload', sa.JSON(), nullable=True),
        sa.Column('error_details', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_background_jobs_user_id', 'background_jobs', ['user_id'])
    op.create_index('ix_background_jobs_dataset_id', 'background_jobs', ['dataset_id'])

    # ML Readiness Reports table
    op.create_table(
        'ml_readiness_reports',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('dataset_id', sa.String(36), sa.ForeignKey('datasets.id', ondelete='CASCADE'), nullable=False),
        sa.Column('version_id', sa.String(36), sa.ForeignKey('dataset_versions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('task_type', sa.String(64), nullable=False),
        sa.Column('target_column', sa.String(255), nullable=True),
        sa.Column('readiness_score', sa.Float(), nullable=False, default=0.0),
        sa.Column('overall_status', sa.String(32), nullable=False),
        sa.Column('findings', sa.JSON(), nullable=False),
        sa.Column('recommendations', sa.JSON(), nullable=False),
        sa.Column('unresolved_issues', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_ml_readiness_reports_dataset_id', 'ml_readiness_reports', ['dataset_id'])
    op.create_index('ix_ml_readiness_reports_version_id', 'ml_readiness_reports', ['version_id'])

def downgrade() -> None:
    op.drop_table('ml_readiness_reports')
    op.drop_table('background_jobs')
    op.drop_table('validation_reports')
    op.drop_table('transformation_runs')
    op.drop_table('dataset_schemas')
    op.drop_table('dataset_versions')
    op.drop_table('datasets')
    op.drop_table('users')
