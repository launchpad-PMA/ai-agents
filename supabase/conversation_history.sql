-- Conversation history for Aragamago.
-- Run once in the Supabase SQL editor. No database password is required.
-- The Railway bot uses the publishable key, which signs in as the anon role,
-- so RLS must allow that role. Keep the publishable key on Railway, not in the phone app.

create table if not exists public.conversation_history (
  id bigint generated always as identity primary key,
  chat_id text not null,
  role text not null,
  content text not null,
  created_at timestamptz not null default now()
);

create index if not exists conversation_history_chat_id_created_at_idx
  on public.conversation_history (chat_id, created_at desc);

alter table public.conversation_history enable row level security;

grant select, insert on public.conversation_history to anon;

drop policy if exists conversation_history_anon_read on public.conversation_history;
create policy conversation_history_anon_read
  on public.conversation_history
  for select
  to anon
  using (true);

drop policy if exists conversation_history_anon_insert on public.conversation_history;
create policy conversation_history_anon_insert
  on public.conversation_history
  for insert
  to anon
  with check (true);
