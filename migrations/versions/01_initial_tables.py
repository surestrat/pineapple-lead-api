"""Initial tables

Revision ID: 01_initial_tables
Revises:
Create Date: 2023-10-03

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "01_initial_tables"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table based on the provided schema
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("first_name", sa.String(), nullable=True),
        sa.Column("last_name", sa.String(), nullable=True),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column("id_number", sa.String(), nullable=True),
        sa.Column("contact_number", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create quotes table based on the provided schema
    op.create_table(
        "quotes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("external_reference_id", sa.String(), nullable=True),
        sa.Column("source", sa.String(), nullable=True),
        sa.Column("quote_id", sa.String(), nullable=True),
        sa.Column("premium", sa.Numeric(), nullable=True),
        sa.Column("excess", sa.Numeric(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create leads table based on the provided schema
    op.create_table(
        "leads",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("source", sa.String(), nullable=True),
        sa.Column("quote_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["quote_id"],
            ["quotes.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create vehicles table based on the provided schema
    op.create_table(
        "vehicles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.Column("make", sa.String(), nullable=True),
        sa.Column("model", sa.String(), nullable=True),
        sa.Column("mm_code", sa.String(), nullable=True),
        sa.Column("modified", sa.Boolean(), nullable=True),
        sa.Column("category", sa.String(), nullable=True),
        sa.Column("colour", sa.String(), nullable=True),
        sa.Column("engine_size", sa.Numeric(), nullable=True),
        sa.Column("financed", sa.Boolean(), nullable=True),
        sa.Column("owner", sa.Boolean(), nullable=True),
        sa.Column("status", sa.String(), nullable=True),
        sa.Column("party_is_regular_driver", sa.Boolean(), nullable=True),
        sa.Column("accessories", sa.Boolean(), nullable=True),
        sa.Column("accessories_amount", sa.Numeric(), nullable=True),
        sa.Column("retail_value", sa.Numeric(), nullable=True),
        sa.Column("market_value", sa.Numeric(), nullable=True),
        sa.Column("insured_value_type", sa.String(), nullable=True),
        sa.Column("use_type", sa.String(), nullable=True),
        sa.Column("overnight_parking_situation", sa.String(), nullable=True),
        sa.Column("cover_code", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create addresses table based on the provided schema
    op.create_table(
        "addresses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("vehicle_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("address_line", sa.String(), nullable=True),
        sa.Column("postal_code", sa.Integer(), nullable=True),
        sa.Column("suburb", sa.String(), nullable=True),
        sa.Column("latitude", sa.Numeric(), nullable=True),
        sa.Column("longitude", sa.Numeric(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["vehicle_id"],
            ["vehicles.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create drivers table based on the provided schema
    op.create_table(
        "drivers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("vehicle_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("marital_status", sa.String(), nullable=True),
        sa.Column("currently_insured", sa.Boolean(), nullable=True),
        sa.Column("years_without_claims", sa.Integer(), nullable=True),
        sa.Column("relation_to_policy_holder", sa.String(), nullable=True),
        sa.Column("email_address", sa.String(), nullable=True),
        sa.Column("mobile_number", sa.String(), nullable=True),
        sa.Column("id_number", sa.String(), nullable=True),
        sa.Column("prv_ins_losses", sa.Integer(), nullable=True),
        sa.Column("license_issue_date", sa.Date(), nullable=True),
        sa.Column("date_of_birth", sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["vehicle_id"],
            ["vehicles.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("drivers")
    op.drop_table("addresses")
    op.drop_table("vehicles")
    op.drop_table("leads")
    op.drop_table("quotes")
    op.drop_table("users")
