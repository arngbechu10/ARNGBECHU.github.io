-- ================================================================
-- Arngbechu Racing 1등 리플레이 (Supabase > SQL Editor에서 한 번 실행)
-- 맵마다 1등 주행 1개만 저장해요(서버 부담 작음). 게임 키로는 표에 직접 쓰지 못하고,
-- submit_replay 함수만 부를 수 있어요. 함수가 "진짜 그 맵 1등 기록인지" 확인한 뒤에만 저장해요.
-- 여러 번 실행해도 괜찮아요. 새 맵 id를 추가하면 아래 맵 목록도 고쳐야 해요!
-- ================================================================

create table if not exists replays (
  map        text primary key,
  name       text not null,
  lap_ms     int  not null,
  car        text,
  data       text not null,
  created_at timestamptz not null default now()
);
alter table replays enable row level security;
drop policy if exists replays_read on replays;
create policy replays_read on replays for select using (true);
revoke insert, update, delete, truncate on replays from anon, authenticated;
grant select on replays to anon, authenticated;

create or replace function submit_replay(p_map text, p_name text, p_lap_ms int, p_car text, p_data text)
returns boolean language plpgsql security definer set search_path = public as $$
declare cur int; md text;
begin
  if p_map not in ('seoul','mountain','xmas','tokyo','ny','pyongyang','touge','coast') then return false; end if;
  -- 오토바이 맵(coast)은 오토바이 순위표(mode='bike')에서 1등인지 봐요
  md := case when p_map in ('coast') then 'bike' else 'lap' end;
  if p_car is null or p_car !~ '^[a-z0-9]{1,12}$' then return false; end if;
  if p_data is null or length(p_data) < 50 or length(p_data) > 700000 or p_data !~ '^[0-9]{2,4}\|[A-Za-z0-9+/=]+$' then return false; end if;
  -- 방금(10분 안) 올라온 같은 이름·같은 시간의 진짜 기록이 있어야 해요
  if not exists (select 1 from scores where mode = md and map = p_map and lap_ms = p_lap_ms
                 and lower(btrim(name)) = lower(btrim(p_name)) and created_at > now() - interval '10 minutes') then return false; end if;
  -- 그 맵에서 더 빠른 기록이 없어야 해요 (= 1등)
  if exists (select 1 from scores where mode = md and map = p_map and lap_ms < p_lap_ms) then return false; end if;
  select lap_ms into cur from replays where map = p_map;
  if cur is not null and cur < p_lap_ms then return false; end if;
  insert into replays(map, name, lap_ms, car, data) values (p_map, btrim(p_name), p_lap_ms, p_car, p_data)
  on conflict (map) do update set name = excluded.name, lap_ms = excluded.lap_ms, car = excluded.car, data = excluded.data, created_at = now();
  return true;
end $$;
revoke all on function submit_replay(text, text, int, text, text) from public;
grant execute on function submit_replay(text, text, int, text, text) to anon, authenticated;

-- (참고) 리플레이 지우기(관리자):  delete from replays where map = 'touge';
