"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-07-07
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0001_initial_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("telegram_chat_id", sa.String(length=64), nullable=True),
        sa.Column("preferred_currency", sa.String(length=3), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.create_table(
        "watchlists",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column(
            "trip_type",
            sa.Enum("ONE_WAY", "ROUND_TRIP", "MULTI_CITY", native_enum=False, length=20),
            nullable=False,
        ),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("max_price", sa.Numeric(12, 2), nullable=True),
        sa.Column("max_stops", sa.Integer(), nullable=False),
        sa.Column("max_duration_minutes", sa.Integer(), nullable=True),
        sa.Column(
            "cabin_class",
            sa.Enum(
                "ECONOMY", "PREMIUM_ECONOMY", "BUSINESS", "FIRST", native_enum=False, length=24
            ),
            nullable=False,
        ),
        sa.Column("adults", sa.Integer(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("check_frequency_hours", sa.Integer(), nullable=False),
        sa.Column("alert_below_max_price", sa.Boolean(), nullable=False),
        sa.Column("alert_below_average_percent", sa.Numeric(5, 2), nullable=True),
        sa.Column("alert_on_new_minimum", sa.Boolean(), nullable=False),
        sa.Column("alert_cooldown_hours", sa.Integer(), nullable=False),
        sa.Column("last_checked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("adults >= 1", name=op.f("ck_watchlists_adults_positive")),
        sa.CheckConstraint(
            "alert_below_average_percent IS NULL OR alert_below_average_percent > 0",
            name=op.f("ck_watchlists_alert_average_percent_positive"),
        ),
        sa.CheckConstraint(
            "alert_cooldown_hours >= 0", name=op.f("ck_watchlists_alert_cooldown_non_negative")
        ),
        sa.CheckConstraint(
            "check_frequency_hours >= 1", name=op.f("ck_watchlists_check_frequency_positive")
        ),
        sa.CheckConstraint(
            "max_duration_minutes IS NULL OR max_duration_minutes > 0",
            name=op.f("ck_watchlists_duration_positive"),
        ),
        sa.CheckConstraint(
            "max_price IS NULL OR max_price > 0", name=op.f("ck_watchlists_max_price_positive")
        ),
        sa.CheckConstraint("max_stops >= 0", name=op.f("ck_watchlists_max_stops_non_negative")),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_watchlists_user_id_users"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_watchlists")),
    )
    op.create_index("ix_watchlists_active", "watchlists", ["active"])
    op.create_index("ix_watchlists_last_checked_at", "watchlists", ["last_checked_at"])
    op.create_index("ix_watchlists_trip_type", "watchlists", ["trip_type"])
    op.create_index("ix_watchlists_user_id", "watchlists", ["user_id"])

    op.create_table(
        "provider_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "provider",
            sa.Enum("MOCK", "AMADEUS", "SKYSCANNER", "DUFFEL", native_enum=False, length=20),
            nullable=False,
        ),
        sa.Column("watchlist_id", sa.Integer(), nullable=True),
        sa.Column("request_hash", sa.String(length=128), nullable=True),
        sa.Column(
            "status", sa.Enum("SUCCESS", "ERROR", native_enum=False, length=20), nullable=False
        ),
        sa.Column("status_code", sa.Integer(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["watchlist_id"],
            ["watchlists.id"],
            name=op.f("fk_provider_logs_watchlist_id_watchlists"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_provider_logs")),
    )
    op.create_index("ix_provider_logs_created_at", "provider_logs", ["created_at"])
    op.create_index("ix_provider_logs_provider", "provider_logs", ["provider"])
    op.create_index("ix_provider_logs_request_hash", "provider_logs", ["request_hash"])
    op.create_index("ix_provider_logs_status", "provider_logs", ["status"])
    op.create_index("ix_provider_logs_watchlist_id", "provider_logs", ["watchlist_id"])

    op.create_table(
        "watchlist_origins",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("watchlist_id", sa.Integer(), nullable=False),
        sa.Column("origin_code", sa.String(length=3), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "length(origin_code) = 3", name=op.f("ck_watchlist_origins_origin_code_iata_length")
        ),
        sa.ForeignKeyConstraint(
            ["watchlist_id"],
            ["watchlists.id"],
            name=op.f("fk_watchlist_origins_watchlist_id_watchlists"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_watchlist_origins")),
    )
    op.create_index("ix_watchlist_origins_origin_code", "watchlist_origins", ["origin_code"])
    op.create_index("ix_watchlist_origins_watchlist_id", "watchlist_origins", ["watchlist_id"])
    op.create_index(
        "uq_watchlist_origins_watchlist_id_origin_code",
        "watchlist_origins",
        ["watchlist_id", "origin_code"],
        unique=True,
    )

    op.create_table(
        "watchlist_destinations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("watchlist_id", sa.Integer(), nullable=False),
        sa.Column("destination_code", sa.String(length=3), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "length(destination_code) = 3",
            name=op.f("ck_watchlist_destinations_destination_code_iata_length"),
        ),
        sa.ForeignKeyConstraint(
            ["watchlist_id"],
            ["watchlists.id"],
            name=op.f("fk_watchlist_destinations_watchlist_id_watchlists"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_watchlist_destinations")),
    )
    op.create_index(
        "ix_watchlist_destinations_destination_code", "watchlist_destinations", ["destination_code"]
    )
    op.create_index(
        "ix_watchlist_destinations_watchlist_id", "watchlist_destinations", ["watchlist_id"]
    )
    op.create_index(
        "uq_watchlist_destinations_watchlist_id_destination_code",
        "watchlist_destinations",
        ["watchlist_id", "destination_code"],
        unique=True,
    )

    op.create_table(
        "watchlist_date_windows",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("watchlist_id", sa.Integer(), nullable=False),
        sa.Column("departure_date_from", sa.Date(), nullable=False),
        sa.Column("departure_date_to", sa.Date(), nullable=False),
        sa.Column("return_date_from", sa.Date(), nullable=True),
        sa.Column("return_date_to", sa.Date(), nullable=True),
        sa.Column("min_trip_days", sa.Integer(), nullable=True),
        sa.Column("max_trip_days", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "departure_date_from <= departure_date_to",
            name=op.f("ck_watchlist_date_windows_departure_window_order"),
        ),
        sa.CheckConstraint(
            "return_date_from IS NULL OR return_date_to IS NULL OR return_date_from <= return_date_to",
            name=op.f("ck_watchlist_date_windows_return_window_order"),
        ),
        sa.CheckConstraint(
            "min_trip_days IS NULL OR max_trip_days IS NULL OR min_trip_days <= max_trip_days",
            name=op.f("ck_watchlist_date_windows_trip_days_order"),
        ),
        sa.ForeignKeyConstraint(
            ["watchlist_id"],
            ["watchlists.id"],
            name=op.f("fk_watchlist_date_windows_watchlist_id_watchlists"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_watchlist_date_windows")),
    )
    op.create_index(
        "ix_watchlist_date_windows_departure_date_from",
        "watchlist_date_windows",
        ["departure_date_from"],
    )
    op.create_index(
        "ix_watchlist_date_windows_departure_date_to",
        "watchlist_date_windows",
        ["departure_date_to"],
    )
    op.create_index(
        "ix_watchlist_date_windows_watchlist_id", "watchlist_date_windows", ["watchlist_id"]
    )

    op.create_table(
        "watchlist_segments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("watchlist_id", sa.Integer(), nullable=False),
        sa.Column("segment_order", sa.Integer(), nullable=False),
        sa.Column("origin_code", sa.String(length=3), nullable=False),
        sa.Column("destination_code", sa.String(length=3), nullable=False),
        sa.Column("date_from", sa.Date(), nullable=False),
        sa.Column("date_to", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "date_from <= date_to", name=op.f("ck_watchlist_segments_segment_date_order")
        ),
        sa.CheckConstraint(
            "length(destination_code) = 3",
            name=op.f("ck_watchlist_segments_segment_destination_code_iata_length"),
        ),
        sa.CheckConstraint(
            "length(origin_code) = 3",
            name=op.f("ck_watchlist_segments_segment_origin_code_iata_length"),
        ),
        sa.CheckConstraint(
            "segment_order >= 1", name=op.f("ck_watchlist_segments_segment_order_positive")
        ),
        sa.ForeignKeyConstraint(
            ["watchlist_id"],
            ["watchlists.id"],
            name=op.f("fk_watchlist_segments_watchlist_id_watchlists"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_watchlist_segments")),
    )
    op.create_index(
        "ix_watchlist_segments_destination_code", "watchlist_segments", ["destination_code"]
    )
    op.create_index("ix_watchlist_segments_origin_code", "watchlist_segments", ["origin_code"])
    op.create_index("ix_watchlist_segments_segment_order", "watchlist_segments", ["segment_order"])
    op.create_index("ix_watchlist_segments_watchlist_id", "watchlist_segments", ["watchlist_id"])
    op.create_index(
        "uq_watchlist_segments_watchlist_id_segment_order",
        "watchlist_segments",
        ["watchlist_id", "segment_order"],
        unique=True,
    )

    op.create_table(
        "flight_offers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("watchlist_id", sa.Integer(), nullable=False),
        sa.Column(
            "provider",
            sa.Enum("MOCK", "AMADEUS", "SKYSCANNER", "DUFFEL", native_enum=False, length=20),
            nullable=False,
        ),
        sa.Column("provider_offer_id", sa.String(length=255), nullable=True),
        sa.Column("origin_code", sa.String(length=3), nullable=False),
        sa.Column("destination_code", sa.String(length=3), nullable=False),
        sa.Column(
            "trip_type",
            sa.Enum("ONE_WAY", "ROUND_TRIP", "MULTI_CITY", native_enum=False, length=20),
            nullable=False,
        ),
        sa.Column("departure_date", sa.Date(), nullable=False),
        sa.Column("return_date", sa.Date(), nullable=True),
        sa.Column("total_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("airline_codes", sa.String(length=255), nullable=True),
        sa.Column("stops", sa.Integer(), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=True),
        sa.Column("deep_link", sa.String(length=2048), nullable=True),
        sa.Column("raw_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("found_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["watchlist_id"],
            ["watchlists.id"],
            name=op.f("fk_flight_offers_watchlist_id_watchlists"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_flight_offers")),
    )
    op.create_index("ix_flight_offers_departure_date", "flight_offers", ["departure_date"])
    op.create_index("ix_flight_offers_destination_code", "flight_offers", ["destination_code"])
    op.create_index("ix_flight_offers_found_at", "flight_offers", ["found_at"])
    op.create_index("ix_flight_offers_origin_code", "flight_offers", ["origin_code"])
    op.create_index("ix_flight_offers_provider", "flight_offers", ["provider"])
    op.create_index("ix_flight_offers_return_date", "flight_offers", ["return_date"])
    op.create_index("ix_flight_offers_total_price", "flight_offers", ["total_price"])
    op.create_index("ix_flight_offers_watchlist_id", "flight_offers", ["watchlist_id"])
    op.create_index(
        "uq_flight_offer_dedupe",
        "flight_offers",
        [
            "watchlist_id",
            "provider",
            "origin_code",
            "destination_code",
            "departure_date",
            "return_date",
            "total_price",
            "airline_codes",
            "stops",
        ],
        unique=True,
    )

    op.create_table(
        "alerts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("watchlist_id", sa.Integer(), nullable=False),
        sa.Column("flight_offer_id", sa.Integer(), nullable=False),
        sa.Column(
            "alert_type",
            sa.Enum(
                "BELOW_MAX_PRICE",
                "BELOW_HISTORICAL_AVERAGE",
                "NEW_HISTORICAL_MINIMUM",
                "CUSTOM_RULE",
                native_enum=False,
                length=32,
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "CANDIDATE",
                "PENDING",
                "SENT",
                "FAILED",
                "SKIPPED_DUPLICATE",
                "SKIPPED_RULE_MISMATCH",
                native_enum=False,
                length=32,
            ),
            nullable=False,
        ),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("sent_to", sa.String(length=255), nullable=True),
        sa.Column(
            "sent_channel",
            sa.Enum("TELEGRAM", "EMAIL", native_enum=False, length=20),
            nullable=True,
        ),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["flight_offer_id"],
            ["flight_offers.id"],
            name=op.f("fk_alerts_flight_offer_id_flight_offers"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["watchlist_id"],
            ["watchlists.id"],
            name=op.f("fk_alerts_watchlist_id_watchlists"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_alerts")),
    )
    op.create_index("ix_alerts_alert_type", "alerts", ["alert_type"])
    op.create_index("ix_alerts_created_at", "alerts", ["created_at"])
    op.create_index("ix_alerts_flight_offer_id", "alerts", ["flight_offer_id"])
    op.create_index("ix_alerts_sent_at", "alerts", ["sent_at"])
    op.create_index("ix_alerts_status", "alerts", ["status"])
    op.create_index("ix_alerts_watchlist_id", "alerts", ["watchlist_id"])
    op.create_index(
        "uq_alerts_watchlist_offer_type_channel",
        "alerts",
        ["watchlist_id", "flight_offer_id", "alert_type", "sent_channel"],
        unique=True,
    )

    op.create_table(
        "price_snapshots",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("watchlist_id", sa.Integer(), nullable=False),
        sa.Column("flight_offer_id", sa.Integer(), nullable=False),
        sa.Column("price", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("checked_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["flight_offer_id"],
            ["flight_offers.id"],
            name=op.f("fk_price_snapshots_flight_offer_id_flight_offers"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["watchlist_id"],
            ["watchlists.id"],
            name=op.f("fk_price_snapshots_watchlist_id_watchlists"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_price_snapshots")),
    )
    op.create_index("ix_price_snapshots_checked_at", "price_snapshots", ["checked_at"])
    op.create_index("ix_price_snapshots_flight_offer_id", "price_snapshots", ["flight_offer_id"])
    op.create_index("ix_price_snapshots_price", "price_snapshots", ["price"])
    op.create_index("ix_price_snapshots_watchlist_id", "price_snapshots", ["watchlist_id"])


def downgrade() -> None:
    op.drop_table("price_snapshots")
    op.drop_table("alerts")
    op.drop_table("flight_offers")
    op.drop_table("watchlist_segments")
    op.drop_table("watchlist_date_windows")
    op.drop_table("watchlist_destinations")
    op.drop_table("watchlist_origins")
    op.drop_table("provider_logs")
    op.drop_table("watchlists")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
