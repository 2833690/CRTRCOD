import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    op.create_table(
        "strategies",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("version", sa.String(20), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="research"),
        sa.Column("config", postgresql.JSONB),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )
    op.create_table(
        "backtest_runs",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("strategy_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("strategies.id")),
        sa.Column("params", postgresql.JSONB, nullable=False),
        sa.Column("metrics", postgresql.JSONB),
        sa.Column("start_date", sa.Date, nullable=False),
        sa.Column("end_date", sa.Date, nullable=False),
        sa.Column("run_ts", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("mlflow_run_id", sa.String(100)),
        sa.Column("status", sa.String(20), server_default="pending"),
    )
    for table in ["paper_trade_events", "live_trade_events"]:
        cols = [
            sa.Column(
                "id",
                postgresql.UUID(as_uuid=True),
                primary_key=True,
                server_default=sa.text("gen_random_uuid()"),
            ),
            sa.Column("event_type", sa.String(30), nullable=False),
            sa.Column("strategy_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("strategies.id")),
            sa.Column("symbol", sa.String(20), nullable=False),
            sa.Column("signal_ts", sa.DateTime(timezone=True)),
            sa.Column("order_ts", sa.DateTime(timezone=True)),
            sa.Column("fill_ts", sa.DateTime(timezone=True)),
            sa.Column("expected_entry", sa.Numeric(20, 8)),
            sa.Column("simulated_fill", sa.Numeric(20, 8)),
            sa.Column("fill_quality_bps", sa.Numeric(10, 4)),
            sa.Column("position_size", sa.Numeric(20, 8)),
            sa.Column("pnl", sa.Numeric(20, 8)),
            sa.Column("fees_paid", sa.Numeric(20, 8)),
            sa.Column("slippage_cost", sa.Numeric(20, 8)),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        ]
        if table == "live_trade_events":
            cols += [
                sa.Column("exchange_order_id", sa.String(100)),
                sa.Column("actual_fill", sa.Numeric(20, 8)),
                sa.Column("is_paper", sa.Boolean, server_default=sa.text("false")),
            ]
        op.create_table(table, *cols)
    op.create_table(
        "audit_log",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("actor", sa.String(100), nullable=False),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("entity_type", sa.String(50)),
        sa.Column("entity_id", sa.String(100)),
        sa.Column("before_value", postgresql.JSONB),
        sa.Column("after_value", postgresql.JSONB),
        sa.Column("reason", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )
    op.create_table(
        "operator_approvals",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("strategy_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("strategies.id")),
        sa.Column("approval_type", sa.String(50), nullable=False),
        sa.Column("operator", sa.String(100), nullable=False),
        sa.Column("notes", sa.Text),
        sa.Column("checklist_state", postgresql.JSONB),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )
    op.create_table(
        "risk_config",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("key", sa.String(100), nullable=False, unique=True),
        sa.Column("value", sa.Text, nullable=False),
        sa.Column("updated_by", sa.String(100)),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )
    op.create_table(
        "signal_candidates",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("strategy_id", sa.String(100), nullable=False),
        sa.Column("params", postgresql.JSONB, nullable=False),
        sa.Column("stability_score", sa.Numeric(5, 2)),
        sa.Column("in_sample_metrics", postgresql.JSONB),
        sa.Column("oos_metrics", postgresql.JSONB),
        sa.Column("walk_forward_result", postgresql.JSONB),
        sa.Column("status", sa.String(20), server_default="candidate"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )


def downgrade():
    for t in [
        "signal_candidates",
        "risk_config",
        "operator_approvals",
        "audit_log",
        "live_trade_events",
        "paper_trade_events",
        "backtest_runs",
        "strategies",
    ]:
        op.drop_table(t)
