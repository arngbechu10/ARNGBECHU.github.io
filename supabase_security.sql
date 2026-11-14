-- ================================================================
-- Arngbechu Racing 순위표 보안 강화 (Supabase > SQL Editor에서 한 번 실행)
-- 게임 안의 공개 키로는 누구나 기록을 "올릴" 수 있어요. 그래서 서버가 이상한 기록을 거절하게 만들어요.
-- 이미 있는 기록은 지우지 않아요(NOT VALID: 새로 올라오는 기록만 검사).
-- 여러 번 실행해도 괜찮아요.
-- ================================================================

-- 0) 올린 시각 열 (도배 막기에 필요)
alter table scores add column if not exists created_at timestamptz not null default now();

-- 1) 이름: 1~20자, 이상한 문자(<, >, 제어 문자) 금지, 욕설 금지
alter table scores drop constraint if exists scores_name_ok;
alter table scores add constraint scores_name_ok check (
  char_length(btrim(name)) between 1 and 20
  and name !~ '[<>\x00-\x1f]'
  and lower(name) !~ '(시발|씨발|씨빨|ㅅㅂ|ㅆㅂ|병신|ㅂㅅ|좆|존나|지랄|fuck|shit|bitch)'
) not valid;

-- 2) 기록 시간: 20초 ~ 1시간 (0.001초 같은 가짜 기록 거절)
alter table scores drop constraint if exists scores_time_ok;
alter table scores add constraint scores_time_ok check (lap_ms between 20000 and 3600000) not valid;

-- 3) 맵·모드·스테이지: 게임에 있는 값만
alter table scores drop constraint if exists scores_kind_ok;
alter table scores add constraint scores_kind_ok check (
  (mode = 'lap'  and map in ('seoul','mountain','xmas','tokyo','ny') and stage is null)
  or (mode = 'hard' and map = 'hard' and stage between 1 and 6)
) not valid;

-- 4) 도배 막기: 같은 이름은 20초에 1번, 전체는 1분에 40번까지
create or replace function scores_rate_limit() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  new.created_at := now();   -- 올리는 사람이 시각을 속이지 못하게
  if exists (select 1 from scores where lower(btrim(name)) = lower(btrim(new.name)) and created_at > now() - interval '20 seconds') then
    raise exception 'too many scores for this name';
  end if;
  if (select count(*) from scores where created_at > now() - interval '1 minute') >= 40 then
    raise exception 'too many scores';
  end if;
  return new;
end $$;
drop trigger if exists scores_rate_limit on scores;
create trigger scores_rate_limit before insert on scores for each row execute function scores_rate_limit();

-- 5) 게임 키로는 기록을 고치거나 지우지 못하게 (보기·올리기만)
revoke update, delete, truncate on scores from anon, authenticated;
alter table scores enable row level security;

-- ----------------------------------------------------------------
-- (참고) 장난 기록 찾기: 아래를 실행하면 의심스러운 기록이 나와요.
--   select id, name, lap_ms, map, mode, stage from scores
--   where lap_ms < 20000 or char_length(name) > 20 order by lap_ms;
-- 지우려면 Table Editor에서 그 줄을 선택하고 Delete를 누르세요(관리자만 가능).
-- ----------------------------------------------------------------
