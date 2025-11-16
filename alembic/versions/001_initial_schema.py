"""Initial schema

Revision ID: 001
Revises:
Create Date: 2025-01-16 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql, sqlite

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create projects table
    op.create_table(
        'projects',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('problem_type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('specification_file', sa.String(length=512), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_projects_status'), 'projects', ['status'])

    # Create experiments table
    op.create_table(
        'experiments',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('project_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('config', sa.JSON(), nullable=False),
        sa.Column('specification_file', sa.String(length=512), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('paused_at', sa.DateTime(), nullable=True),
        sa.Column('iterations_completed', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('best_score', sa.Float(), nullable=True),
        sa.Column('best_program', sa.Text(), nullable=True),
        sa.Column('mlflow_run_id', sa.String(length=100), nullable=True),
        sa.Column('task_id', sa.String(length=100), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_experiments_project_id'), 'experiments', ['project_id'])
    op.create_index(op.f('ix_experiments_status'), 'experiments', ['status'])
    op.create_index(op.f('ix_experiments_mlflow_run_id'), 'experiments', ['mlflow_run_id'])
    op.create_index(op.f('ix_experiments_started_at'), 'experiments', ['started_at'])


def downgrade() -> None:
    op.drop_index(op.f('ix_experiments_started_at'), table_name='experiments')
    op.drop_index(op.f('ix_experiments_mlflow_run_id'), table_name='experiments')
    op.drop_index(op.f('ix_experiments_status'), table_name='experiments')
    op.drop_index(op.f('ix_experiments_project_id'), table_name='experiments')
    op.drop_table('experiments')
    op.drop_index(op.f('ix_projects_status'), table_name='projects')
    op.drop_table('projects')
