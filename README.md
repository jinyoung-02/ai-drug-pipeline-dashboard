# AI 신약 파이프라인 경쟁사 트래킹 대시보드

인실리코 메디슨, 리커전 파마슈티컬스 등 **AI 네이티브 신약개발 기업**들의 파이프라인 진행 현황(회사·타겟·기전·개발단계)을 트래킹하는 대시보드입니다. 보조 섹션으로 공개 화합물 벤치마크(ClinTox/HIV/Tox21/BACE) 데이터를 함께 제공합니다.

자세한 배경·요구사항·데이터 처리 규칙은 [PRD_AI신약파이프라인_트래킹_대시보드.md](PRD_AI신약파이프라인_트래킹_대시보드.md)를 참고하세요.

## 주요 화면

- **개요**: 총 후보물질 수, 참여 기업 수, 최고 진행단계, 상용화 완료 건수(0건) 등 KPI
- **파이프라인 트래커**: 회사·개발단계·기전/적응증 키워드로 필터링 가능한 후보물질 테이블
- **개발단계 퍼널**: 전임상 → Phase I → Phase I/II → Phase III → 상용화 단계별 분포, 중단 건 별도 표시
- **회사 비교**: 회사별 후보물질 수, 최고 진행단계, 대표 AI 플랫폼 비교
- **최신 마일스톤**: 기준일(as_of_date) 내림차순 타임라인, 출처 링크 포함
- **화합물 벤치마크(참고)**: 공개 벤치마크 데이터셋의 승인/독성실패/미분류 화합물 물성 비교 — 위 경쟁사 파이프라인과 직접 연결되지 않는 참고 자료

> 10개 후보물질·5개 기업 스냅샷으로 업계 전체를 대표하지 않으며, 각 행의 기준일이 서로 다릅니다. 화합물 벤치마크 섹션은 자사 실제 파이프라인이 아닌 공개 데이터임에 유의하세요.

## 사용 방법

로그인·서버·빌드 도구 없이 [index.html](index.html) 하나만 열면 됩니다. 데이터는 Supabase(Postgres)에서 브라우저가 직접 읽어옵니다.

- 로컬에서 보기: `index.html`을 브라우저로 더블클릭해서 열기 (네트워크 연결 필요 — Supabase REST 호출)
- GitHub Pages로 배포하는 경우: 저장소 루트를 Pages 소스로 지정하면 `index.html`이 그대로 루트 경로에서 열립니다.
- `index.html`에는 Supabase **anon key**가 그대로 노출됩니다. 이 키는 RLS로 `SELECT`만 허용되도록 설정되어 있어 공개해도 안전합니다 (`data/schema.sql` 참고). 쓰기 권한이 있는 service role key는 절대 이 파일에 넣지 않습니다.

## 데이터 갱신

원본 CSV(`source_data/ai_drug_pipeline_candidates.csv`, `source_data/drug_candidates_master.csv`)를 교체해서 `main`에 push하면, GitHub Actions(`.github/workflows/sync-data.yml`)가 자동으로 Supabase 테이블에 upsert합니다. `index.html`은 재생성/재배포가 필요 없고, 브라우저를 새로고침하면 바로 최신 데이터가 보입니다.

로컬에서 즉시 반영하고 싶다면:

```bash
SUPABASE_URL=... SUPABASE_SERVICE_ROLE_KEY=... python3 scripts/sync_to_supabase.py
```

Python 표준 라이브러리(`csv`, `json`, `os`, `urllib.request`)만 사용하므로 별도 설치가 필요 없습니다. 처음 설정할 때는 `data/schema.sql`을 Supabase SQL Editor에서 1회 실행해 테이블/RLS 정책을 만들어야 합니다.

## 파일 구조

```
index.html                          최종 대시보드 (배포 대상, Supabase에서 데이터를 fetch)
scripts/sync_to_supabase.py         CSV → Supabase 테이블 upsert 스크립트
scripts/index_template.html         HTML/CSS/JS 템플릿 (마크업·렌더링·집계 로직 수정은 여기서)
source_data/                         원본 CSV 2개 (ai_drug_pipeline_candidates.csv, drug_candidates_master.csv)
data/schema.sql                      Supabase 테이블 생성 + RLS 정책 (최초 1회 실행)
.github/workflows/sync-data.yml      source_data/*.csv push 시 Supabase 자동 동기화
PRD_AI신약파이프라인_트래킹_대시보드.md   요구사항/데이터 처리 규칙 원본
PROMPT_AI신약파이프라인_대시보드_재현.md  재현용 프롬프트 요약 문서
```

## 기술 스택

순수 HTML/CSS/JS 단일 파일. 외부 라이브러리 의존성을 최소화하기 위해 차트는 CSS 기반 바 형태로 직접 구현했고(Chart.js 미사용), 폰트만 Pretendard를 CDN에서 로드합니다.

## 데이터 개요

- **ai_drug_pipeline_candidates.csv**: 10개 후보물질, 5개 기업(Insilico Medicine, Recursion Pharmaceuticals, Exscientia/Recursion 합병, Iambic Therapeutics, Isomorphic Labs)
- **drug_candidates_master.csv**: 공개 ML 벤치마크 4종(ClinTox 60·HIV 60·Tox21 59·BACE 12) 화합물 191개, SMILES/물성치/독성/효능 지표 포함
- 두 파일은 서로 다른 성격의 데이터이며 연결 키가 없어 조인하지 않고 독립 섹션으로 다룹니다.
