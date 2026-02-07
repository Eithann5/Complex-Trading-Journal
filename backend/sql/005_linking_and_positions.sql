-- Mission 005: linking + position journal tables

create extension if not exists pgcrypto;

create table if not exists position_journal (
    id uuid primary key default gen_random_uuid(),
    ticker text not null,
    status text not null default 'open' check (status in ('open', 'closed')),
    open_time_utc timestamptz null,
    close_time_utc timestamptz null,
    origin text not null default 'manual' check (origin in ('manual', 'alert_based')),
    notes text null,
    created_at timestamptz not null default timezone('utc', now())
);

create table if not exists trigger_position_links (
    id uuid primary key default gen_random_uuid(),
    trigger_id uuid not null references alerts_triggers(id) on delete cascade,
    position_id uuid not null references position_journal(id) on delete cascade,
    link_type text not null check (link_type in ('trigger', 'context', 'post_entry')),
    created_at timestamptz not null default timezone('utc', now()),
    created_by text null,
    unique (trigger_id, position_id, link_type)
);

create table if not exists position_tags (
    id uuid primary key default gen_random_uuid(),
    position_id uuid not null references position_journal(id) on delete cascade,
    tag text not null,
    source text not null default 'manual' check (source in ('manual', 'auto')),
    created_at timestamptz not null default timezone('utc', now())
);

create index if not exists idx_position_journal_status
    on position_journal(status);

create index if not exists idx_trigger_position_links_trigger_id
    on trigger_position_links(trigger_id);

create index if not exists idx_trigger_position_links_position_id
    on trigger_position_links(position_id);

create index if not exists idx_position_tags_position_id
    on position_tags(position_id);
