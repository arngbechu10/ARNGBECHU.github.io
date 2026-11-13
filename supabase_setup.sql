-- Supabase > SQL Editor 에서 한 번만 실행하세요.
-- 기존 기록은 그대로 두고 (Seoul / 개인 랩타임으로 취급) 새 열만 추가합니다.
alter table scores add column if not exists map   text not null default 'seoul';
alter table scores add column if not exists mode  text not null default 'lap';
alter table scores add column if not exists stage int;
-- 하드모드 기록: mode='hard', map='hard', stage=클리어한 스테이지 수, lap_ms=누적 시간
-- 기존 select / insert 정책(RLS)은 그대로 쓰면 됩니다.
