create table if not exists public.telegram_messages (
    id bigint generated always as identity primary key,
    telegram_update_id bigint not null unique,
    telegram_message_id bigint not null,
    chat_id bigint not null,
    chat_type text not null,
    from_user_id bigint,
    username text,
    first_name text,
    last_name text,
    content_type text not null,
    message_text text,
    caption text,
    message_date timestamptz not null,
    received_at timestamptz not null default now()
);

alter table public.telegram_messages enable row level security;

-- No public/anon policies are added. The server-only service_role key bypasses
-- Row Level Security, so keep it exclusively in Replit Secrets.