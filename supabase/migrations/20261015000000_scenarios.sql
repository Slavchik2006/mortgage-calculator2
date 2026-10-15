-- Saved scenarios, scoped by an anonymous per-browser session id (no user accounts).
-- Only the backend (service-role key) touches this table: RLS is on with no policies,
-- and all privileges are revoked from the public API roles.
create table public.scenarios (
  id         uuid primary key default gen_random_uuid(),
  session_id uuid not null,
  name       text not null check (char_length(name) between 1 and 60),
  inputs     jsonb not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index scenarios_session_idx on public.scenarios (session_id, updated_at desc);

alter table public.scenarios enable row level security;
revoke all on public.scenarios from anon, authenticated;

create function public.set_updated_at() returns trigger
language plpgsql
set search_path = ''
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

create trigger scenarios_set_updated_at
  before update on public.scenarios
  for each row execute function public.set_updated_at();
