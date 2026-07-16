-- Supabase SQL Editor에서 1회 실행. pipeline_candidates / benchmark_compounds 테이블 생성 + 읽기 전용 RLS.

create table if not exists pipeline_candidates (
  id bigint generated always as identity primary key,
  company text not null,
  candidate_name text not null,
  target_mechanism text,
  indication text,
  ai_discovery_approach text,
  current_stage text,
  commercialized text,
  key_milestone_note text,
  source_url text,
  as_of_date text,
  unique (company, candidate_name)
);

create table if not exists benchmark_compounds (
  compound_id text primary key,
  source_dataset text,
  input_smiles text,
  canonical_smiles text,
  mw double precision,
  logp double precision,
  hbd double precision,
  hba double precision,
  tpsa double precision,
  rotatable_bonds double precision,
  qed_druglikeness double precision,
  lipinski_violations double precision,
  toxicity_flag text,
  toxicity_assay text,
  fda_approved text,
  developed_status text,
  efficacy_assay text,
  efficacy_value text,
  efficacy_active_flag text
);

alter table pipeline_candidates enable row level security;
alter table benchmark_compounds enable row level security;

create policy "public read pipeline_candidates" on pipeline_candidates
  for select using (true);

create policy "public read benchmark_compounds" on benchmark_compounds
  for select using (true);

-- INSERT/UPDATE 정책은 만들지 않음: anon key로는 쓰기 불가, service role key(GitHub Actions secret)만 RLS를 우회해 쓸 수 있음.
