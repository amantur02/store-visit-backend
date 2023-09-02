"""create_orders_visits

Revision ID: 82b384d0c544
Revises: bf983eebfb5c
Create Date: 2023-09-01 18:35:47.448232

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '82b384d0c544'
down_revision = 'bf983eebfb5c'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("DROP TYPE IF EXISTS order_status_enum;")
    op.execute(
        "CREATE TYPE order_status_enum as ENUM('started', 'ended', 'in_process', 'awaiting', 'canceled');"
    )
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('stores',
                    sa.Column('title', sa.String(length=255), nullable=False),
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('is_deleted', sa.Boolean(), server_default=sa.text('false'), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_stores_id'), 'stores', ['id'], unique=False)
    op.create_table('orders',
                    sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'),
                              nullable=False),
                    sa.Column('expires_at', sa.TIMESTAMP(), nullable=True),
                    sa.Column('store_id', sa.Integer(), nullable=False),
                    sa.Column('customer_id', sa.Integer(), nullable=False),
                    sa.Column('status', postgresql.ENUM('started', 'ended', 'in_process', 'awaiting', 'canceled',
                                                        name='order_status_enum', create_type=False), nullable=True),
                    sa.Column('worker_id', sa.Integer(), nullable=False),
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('is_deleted', sa.Boolean(), server_default=sa.text('false'), nullable=True),
                    sa.ForeignKeyConstraint(['customer_id'], ['users.id'], ondelete='RESTRICT'),
                    sa.ForeignKeyConstraint(['store_id'], ['stores.id'], ondelete='RESTRICT'),
                    sa.ForeignKeyConstraint(['worker_id'], ['users.id'], ondelete='RESTRICT'),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_orders_id'), 'orders', ['id'], unique=False)
    op.create_table('visits',
                    sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'),
                              nullable=False),
                    sa.Column('worker_id', sa.Integer(), nullable=False),
                    sa.Column('order_id', sa.Integer(), nullable=False),
                    sa.Column('customer_id', sa.Integer(), nullable=False),
                    sa.Column('store_id', sa.Integer(), nullable=False),
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('is_deleted', sa.Boolean(), server_default=sa.text('false'), nullable=True),
                    sa.ForeignKeyConstraint(['customer_id'], ['users.id'], ondelete='RESTRICT'),
                    sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='RESTRICT'),
                    sa.ForeignKeyConstraint(['store_id'], ['stores.id'], ondelete='RESTRICT'),
                    sa.ForeignKeyConstraint(['worker_id'], ['users.id'], ondelete='RESTRICT'),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('order_id')
                    )
    op.create_index(op.f('ix_visits_id'), 'visits', ['id'], unique=False)
    op.add_column('users', sa.Column('store_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'users', 'stores', ['store_id'], ['id'], ondelete='RESTRICT')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'users', type_='foreignkey')
    op.drop_column('users', 'store_id')
    op.drop_index(op.f('ix_visits_id'), table_name='visits')
    op.drop_table('visits')
    op.drop_index(op.f('ix_orders_id'), table_name='orders')
    op.drop_table('orders')
    op.drop_index(op.f('ix_stores_id'), table_name='stores')
    op.drop_table('stores')
    op.execute("DROP TYPE IF EXISTS order_status_enum;")
    # ### end Alembic commands ###