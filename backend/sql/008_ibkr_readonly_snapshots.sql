-- Mission 008: IBKR read-only snapshots table

create extension if not exists pgcrypto;

create table if not exists positions_snapshot (
    id uuid primary key default gen_random_uuid(),
    snapshot_time_utc timestamptz not null default timezone('utc', now()),
    ticker text not null,
    quantity numeric not null,
    avg_cost numeric not null,
    market_price numeric null,
    unrealized_pnl numeric null,
    currency text null,
    raw jsonb not null
);

create index if not exists idx_positions_snapshot_ticker_time
    on positions_snapshot(ticker, snapshot_time_utc desc);
