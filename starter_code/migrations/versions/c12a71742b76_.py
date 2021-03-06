"""empty message

Revision ID: c12a71742b76
Revises: 119bae621cc9
Create Date: 2020-05-16 23:43:24.257563

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c12a71742b76'
down_revision = '119bae621cc9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('shows_artist_id_fkey', 'shows', type_='foreignkey')
    op.drop_constraint('shows_venue_id_fkey', 'shows', type_='foreignkey')
    op.create_foreign_key(None, 'shows', 'venue', ['venue_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'shows', 'artist', ['artist_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'shows', type_='foreignkey')
    op.drop_constraint(None, 'shows', type_='foreignkey')
    op.create_foreign_key('shows_venue_id_fkey', 'shows', 'venue', ['venue_id'], ['id'])
    op.create_foreign_key('shows_artist_id_fkey', 'shows', 'artist', ['artist_id'], ['id'])
    # ### end Alembic commands ###
