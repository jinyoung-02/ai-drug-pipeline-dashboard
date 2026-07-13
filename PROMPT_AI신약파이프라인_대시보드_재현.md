# 재현 프롬프트: AI 신약 파이프라인 경쟁사 트래킹 대시보드

이 문서는 `index.html`을 만들기까지 오간 대화(PRD 인터뷰 → 빌드 → 검증 → 신규 레포 분리)에서 확정된 요구사항을 하나의 프롬프트로 정리한 것이다. 아래 내용을 그대로(또는 데이터만 교체해서) AI 에이전트에게 주면 동일한 결과물을 재현할 수 있어야 한다.

---

## 프롬프트 원문 (그대로 사용)

```
다음 두 CSV를 바탕으로 "AI 신약 파이프라인 경쟁사 트래킹 대시보드"를 단일 HTML 파일로 만들어줘.

# 입력 데이터

## 1) ai_drug_pipeline_candidates.csv (메인 데이터, 10행)
컬럼: company, candidate_name, target_mechanism, indication, ai_discovery_approach,
      current_stage, commercialized, key_milestone_note, source_url, as_of_date

- AI 네이티브 신약개발 기업 5곳(Insilico Medicine, Recursion Pharmaceuticals,
  Exscientia/Recursion 합병, Iambic Therapeutics, Isomorphic Labs)의 후보물질 10건.
- commercialized는 현재 전량 "No" — 상용화 완료 사례가 아직 없다는 것이 핵심 시사점이므로
  하드코딩하지 말고 데이터에서 판정하는 로직으로 처리(향후 값이 바뀔 수 있음).
- current_stage 표기가 영문/한글 혼재, 괄호 부연설명 포함(예: "Early clinical (Phase I/IIa)",
  "중단 (Discontinued)", "전임상/IND 준비 단계(첫 임상 진입 준비 중)") — 정규화 매핑이 필요.
- as_of_date는 행마다 다른 시점("2023-09 (licensed; trial ongoing)" 처럼 괄호 부연설명이
  붙은 값도 있음) — 기준일 "범위"를 표시할 땐 YYYY-MM 접두 7자만 잘라 쓰고, 원문 전체는
  테이블/타임라인 상세에는 그대로 노출할 것.

## 2) drug_candidates_master.csv (보조 데이터, 191행)
컬럼: compound_id, source_dataset, input_smiles, canonical_smiles, mw, logp, hbd, hba,
      tpsa, rotatable_bonds, qed_druglikeness, lipinski_violations, toxicity_flag,
      toxicity_assay, fda_approved, developed_status, efficacy_assay, efficacy_value,
      efficacy_active_flag

- 공개 ML 벤치마크 4종(ClinTox 60 / HIV 60 / Tox21 59 / BACE 12)이 섞인 union 데이터.
- fda_approved는 1(승인)/0(임상 독성실패)/빈값(미분류 원시 스크리닝 화합물) 3분류로 처리.
  빈값을 0으로 취급하지 말 것.
- efficacy_value는 데이터셋마다 형식이 다름 — BACE는 연속형 pIC50 수치, HIV는 범주형
  텍스트(CI/CM) — 집계 시 절대 섞어서 평균 내지 말고 데이터셋별로 분리 처리.
- toxicity_assay는 세미콜론(;)으로 구분된 다중값이 존재(Tox21) — 분해해서 태그로 다룰 것.

**중요: 두 CSV는 서로 연결할 공통 키가 없다.** file1의 경쟁사 후보물질과 file2의 벤치마크
화합물은 매칭되지 않는 완전히 독립된 데이터다. 절대 조인하지 말고, 두 개의 분리된 섹션
(메인 vs 참고)으로 다뤄라.

# 대상 사용자 및 목적
사내 AI 신약개발 연구팀. 1차 목적은 **경쟁사 파이프라인 트래킹**(회사·타겟·개발단계 파악,
경쟁 구도 파악, 내부 보고/공유). 화합물 벤치마크(file2)는 **보조 참고 섹션**으로만 제공
(자사 AI 스크리닝 기준을 세울 때 참고용, 실제 파이프라인과 무관함을 명시).

# 산출물 형식
- 서버·로그인 없는 단일 HTML 파일 (인라인 style/script, 외부 JS/CSS 파일 없음)
- 데이터는 JSON으로 변환해 `const DATA = {...}`로 스크립트에 직접 임베드하는 방식.
  파이썬 표준 라이브러리(csv/json/collections/statistics/pathlib)만 사용하는 빌드
  스크립트로 `__DATA_JSON__` 자리표시자가 있는 HTML 템플릿을 채워 최종 파일을 생성할 것
  (pip install 불필요, 아래 "구현 방식" 참고)
- **차트 라이브러리(Chart.js 등)를 쓰지 말고 순수 CSS/HTML로 바 차트·퍼널을 구현할 것.**
  이유: (a) 사내망처럼 CDN이 막힐 수 있는 환경 대비, (b) `display:none`인 섹션 안의
  canvas가 0×0으로 렌더링되는 문제를 원천적으로 피하기 위함. 폰트(Pretendard)만 CDN에서
  로드하고, 로드 실패해도 시스템 폰트로 자연스럽게 폴백되므로 문제없음.

# 디자인
- 좌측 사이드바 네비게이션 + 우측 콘텐츠 영역, 섹션 전환 방식(라우터 없음, JS로
  `.section.active` 토글, nav-item 클릭 시 전환)
- Wanted Design System(WDS) 토큰 사용: `--blue-*`, `--cn-*`(neutral), `--label-*`,
  `--fill-*`, `--radius-*`, `--shadow-*` 등. 채도 낮은 뉴트럴 배경 위에 파란색 포인트
  컬러(#0066FF 계열), 카드형 패널(둥근 모서리 16px, 얇은 테두리 + 옅은 그림자)

# 상단 고지 배너 (상시 노출)
"이 대시보드는 공개 뉴스·보도자료 기반 10개 후보물질·5개 기업 스냅샷이며 업계 전체를
대표하지 않는다", "각 행의 기준일(as_of_date)이 서로 달라 한 시점 현황이 아니다",
"화합물 벤치마크 섹션은 경쟁사 파이프라인과 직접 연결되지 않는 참고 자료다"를 주황색
배너로 항상 노출. 화합물 벤치마크 섹션 상단에는 별도로 옅은 파란색 안내 배너를 추가로
노출(공개 벤치마크 데이터이며 자사 실제 후보물질이 아님을 재차 강조).

# 대시보드 구성 (사이드바 순서대로, 총 6개 섹션)

## 1. 개요
- KPI 카드 4개: 총 후보물질 수(10), 참여 기업 수(5), 최고 진행단계(Phase III),
  상용화(승인) 완료 건수(0건, 하드코딩 아니고 데이터에서 계산)
- 핵심 시사점 카드(텍스트): "상용화 완료 사례 0건" + 가장 앞선 후보(Rentosertib,
  Phase III) 언급 + 중단 사례 1건 언급
- 개발단계 미니 퍼널(아래 3번과 같은 렌더 함수 재사용)

## 2. 파이프라인 트래커
- 컬럼: 기업, 후보물질명, 타겟/기전, 적응증, AI 접근법, 현재단계(뱃지), 기준일, 출처(링크),
  마일스톤(클릭하면 펼쳐지는 행)
- 필터: 기업 드롭다운, 개발단계 드롭다운, 타겟/기전/적응증 키워드 검색(입력 즉시 필터링)
- 필터링된 건수 / 전체 건수 카운트 노출

## 3. 개발단계 퍼널
- 전임상/IND 준비 → Phase I → Phase I/II → Phase III → 상용화(승인) 순서의 가로 바 차트
  (순수 CSS, 각 바 너비는 최대 건수 대비 비율로 계산, 0건인 단계도 빈 바로 표시)
- "중단(Discontinued)" 건은 퍼널 밖에서 별도 카드로 표시(퍼널에 섞지 말 것)

## 4. 회사 비교
- 회사별 카드: 후보물질 수, 최고 진행단계(뱃지), 중단 건수(있는 경우만 표시), 대표
  후보물질명 목록, AI 접근법/플랫폼 목록
- 최고 진행단계 산정 로직: 중단이 아닌 후보 중 단계 순서(전임상=1~Phase III=4)가 가장
  높은 것. 만약 모든 후보가 중단이면 "중단"으로 표시.

## 5. 최신 마일스톤
- as_of_date 내림차순 타임라인. 날짜, 후보물질명+단계 뱃지, 회사·타겟, 마일스톤 노트,
  출처 링크
- "스냅샷 시점이 행마다 다르다"는 안내 문구를 섹션 설명에 포함

## 6. 화합물 벤치마크 (보조, 참고 섹션 배지 명시)
- KPI 카드: 총 화합물 수, 데이터셋 구성(ClinTox/HIV/Tox21/BACE 개수), 독성 확인 비율
  (toxicity_flag가 채워진 유효 표본 기준), FDA 승인 화합물 수
- 승인/독성실패/미분류 3그룹별 물성 지표(QED, Lipinski 위반, LogP, TPSA, 분자량) 평균
  비교 테이블(표본 수 n도 함께 표시)
- 효능 데이터 보유 화합물(HIV/BACE)의 데이터셋별 활성 비율, 질환/타겟 매핑
  (HIV → "HIV/AIDS", BACE → "알츠하이머병")
- Tox21 다중 독성 어세이 양성 빈도 태그 목록(세미콜론 분해 후 집계, 중복 허용)

# 데이터 처리 규칙

## 개발단계 정규화 (그룹 + 퍼널 순서)
문자열에 아래 키워드가 포함되는지 순서대로 검사해 첫 매칭을 사용:
1. "중단" 또는 "Discontinued" 포함 → 그룹 "중단", 퍼널 순서 없음(퍼널 밖)
2. "Phase III" 포함 → 그룹 "Phase III", 순서 4
3. "Phase I/II" 또는 "Phase I/IIa" 또는 "Early clinical" 포함 → 그룹 "Phase I/II", 순서 3
4. "Phase I/Ib" 포함 → 그룹 "Phase I/Ib", 순서 2
5. "Phase I" 포함 → 그룹 "Phase I", 순서 2
6. "전임상" 또는 "IND" 포함 → 그룹 "전임상/IND 준비", 순서 1

## FDA 승인 3분류
- fda_approved == "1" → "approved"
- fda_approved == "0" → "failed_toxicity"
- 그 외(빈값) → "unclassified" (0으로 취급 금지)

## 결측치 처리
- 화합물 벤치마크 쪽 수치 필드는 값이 없으면 통계 계산에서 제외(0으로 대체 금지)
- 파이프라인 트래커 쪽 표시값이 없으면 "N/A"로 통일 표시

## Tox21 다중 어세이 파싱
- toxicity_assay 값을 ";"로 split, 빈 문자열 제거 후 배열로 다룸. 어세이별 양성 건수
  집계 시 중복 카운트 허용(한 화합물이 여러 어세이에 동시 양성일 수 있음)

## as_of_date 표시
- 상단 KPI/메타에 쓰는 "기준일 범위"는 각 행의 as_of_date 앞 7글자(YYYY-MM)만 취해
  정렬 후 최솟값~최댓값으로 표시(괄호 부연설명이 섞인 원문 그대로 범위에 쓰지 말 것)
- 테이블/타임라인 개별 행에는 as_of_date 원문 전체를 그대로 노출

# 반드시 지켜야 할 기술적 주의사항 (이전 시행착오에서 얻은 교훈)

1. **각 섹션의 초기화 함수 호출은 개별적으로 try/catch로 감쌀 것**
   (`safeInit(name, fn)` 헬퍼 패턴). 한 섹션의 초기화가 실패해도 나머지 섹션은 정상
   렌더링돼야 한다.
2. **차트 라이브러리를 아예 쓰지 않는 방향을 우선 고려하라.** Chart.js 등을 쓰면
   (a) CDN 로드 실패 시 전체가 깨지는 문제, (b) `display:none` 부모 안의 canvas가
   0×0으로 측정되는 문제가 생긴다. 이 프로젝트에서는 모든 차트를 순수 CSS 바로 구현해
   두 문제를 원천 차단했다. 새 차트가 필요하면 먼저 CSS/HTML로 가능한지 검토할 것.
3. **빌드 후 반드시 자동 검증할 것**: (a) 임베드된 `<script>` 블록만 추출해
   `node --check`로 문법 검증, (b) jsdom으로 헤드리스 실행해 각 섹션의 초기 렌더
   (KPI 카드 개수, 테이블 행 수 등), 필터/정렬 동작, nav 섹션 전환, 상세 토글(펼치기)
   동작을 스크립트로 자동 확인. 수동으로 "됐겠지" 하고 넘어가지 말 것.
4. **파일을 두 개의 서로 다른 인터페이스(파일 편집 도구 vs 셸)로 오갈 때 동기화 지연이
   생길 수 있다.** 파일 편집 도구로 스크립트를 수정한 직후 셸에서 바로 실행했더니 수정
   전 내용으로 실행되는 현상이 있었다. 이런 경우 셸에서 heredoc으로 파일을 직접 다시
   쓴 뒤 실행하면 확실하게 반영된다. 빌드 결과가 예상과 다르면 먼저 이 동기화 문제를
   의심할 것.
5. **작업 폴더가 사용자 실제 폴더에 연결된 환경(Cowork류)이라면, 한번 생성된 파일은
   삭제·이름변경이 안 될 수 있다.** 필요 없는 파일을 "일단 복사해두고 나중에 지우자"는
   식으로 접근하면 안 된다 — 복사 시점에 정확히 필요한 파일만 골라 복사할 것. 이미
   잘못 복사된 파일이 있다면 README 등에 "이 파일은 안 씀"이라고 명시하고 사용자가
   직접 정리하도록 안내한다.
6. **같은 이유로, 특정 하위 폴더의 내용이 예고 없이 통째로 비어버리는 현상도 관측됐다**
   (`stat`으로는 폴더가 존재한다고 나오는데 `ls`/`cat`/`open()` 전부 실패하거나, 심지어
   부모 디렉터리 목록에서 폴더 자체가 사라지기도 함 — 동기화 지연이 원인으로 추정).
   원본 CSV를 하위 폴더에 복사해 넣은 뒤에는 **반드시 `md5sum`(또는 동급 체크섬)으로
   원본과 복사본을 대조해 확인**할 것. 만약 특정 경로가 이렇게 깨진 상태로 보이면 같은
   이름으로 재시도하지 말고 **다른 이름의 새 폴더**를 만들어 우회하는 편이 빠르다(이번엔
   `drug_discovery_data/` → `source_data/`로 이름을 바꿔서 해결됨).

# 구현 방식 (권장)
1. 파이썬 표준 라이브러리(csv, json, statistics, collections, pathlib)만으로 빌드
   스크립트 작성:
   - `ai_drug_pipeline_candidates.csv` → 단계 정규화 + 회사별 요약 + 퍼널 집계 +
     마일스톤 정렬
   - `drug_candidates_master.csv` → FDA 3분류 + 그룹별 물성 통계(min/mean/max/n) +
     독성 유효표본 집계 + 데이터셋별 효능 집계 + Tox21 다중 어세이 집계
   - 위 결과를 하나의 JSON(`data/pipeline_data.json`)으로 저장하고, HTML 템플릿의
     `__DATA_JSON__` 자리표시자를 그 JSON 문자열로 치환해 최종 `index.html` 생성
2. HTML 템플릿(`scripts/index_template.html`)에 마크업/스타일/JS 렌더링 로직 작성
3. 빌드 스크립트 실행 → `node --check`로 인라인 스크립트 문법 검증 → jsdom으로
   헤드리스 렌더링 후 각 섹션 DOM 내용·건수, 필터 동작, nav 전환, 행 펼치기 토글을
   자동 검증
```

---

## 데이터셋 프로필 (2026-07-13 기준, 참고용)

### ai_drug_pipeline_candidates.csv
| 회사 | 후보물질 수 | 최고 진행단계 | 중단 |
|---|---|---|---|
| Insilico Medicine | 4 | Phase III (Rentosertib) | 0 |
| Recursion Pharmaceuticals | 3 | Phase I/II | 0 |
| Iambic Therapeutics | 1 | Phase I/Ib | 0 |
| Isomorphic Labs (Alphabet/DeepMind 계열) | 1 | 전임상/IND 준비 | 0 |
| Exscientia (Recursion 합병) | 1 | — | 1 (EXS-21546) |

퍼널 집계: 전임상/IND준비 1건 · Phase I 3건 · Phase I/II 4건 · Phase III 1건 · 상용화 0건 · 중단 1건 (합계 10건)

as_of_date 범위: 2023-09 ~ 2026-07 / 상용화(commercialized="Yes") 0건

### drug_candidates_master.csv
- 총 191개 화합물, 소스: ClinTox 60 / Tox21 59 / HIV 60 / BACE 12
- fda_approved 3분류: 승인 57 / 임상 독성실패 3 / 미분류 131
- 승인 그룹 qed_druglikeness 평균 0.385(n=57), 독성실패 그룹 평균 0.453(n=3), 미분류 그룹 평균 0.509(n=131)
- 독성 유효표본(toxicity_flag 존재) 119건 중 양성 22건 (약 18.5%)
- 효능 데이터: HIV 60건 중 활성 2건, BACE 12건 중 활성 12건(전량)
- 독성×효능 동시 보유 화합물: 0개 (두 지표가 소스 데이터셋별로 완전히 분리되어 있음)

---

## 대화 중 변경 이력

1. **PRD 인터뷰**: 질의응답 2라운드로 스코프 확정 — (a) 핵심 목적 = 경쟁사 파이프라인
   트래킹(파일1 메인), (b) drug_candidates_master.csv(파일2)는 보조 섹션으로 포함,
   (c) 산출물은 서버·로그인 없는 단일 HTML — `PRD_AI신약파이프라인_트래킹_대시보드.md` 작성
2. **기존 산출물 발견**: 같은 프로젝트 폴더(`source_data/`)에 이미 다른 스코프
   (화합물 벤치마크만 다루는 "스크리닝" 대시보드)의 PRD·목업이 존재함을 확인. 사용자
   확인 후 오늘 PRD 기준으로 새 대시보드를 별도 제작하기로 결정(기존 목업은 디자인
   토큰/기술 패턴 참고용으로만 활용, 데이터·스코프는 재사용하지 않음)
3. **빌드 스크립트 작성**: `scripts/build_pipeline_dashboard.py` — 표준 라이브러리만
   사용, 단계 정규화/회사 요약/퍼널/화합물 벤치마크 통계 계산 후 JSON 생성
4. **HTML 템플릿 작성**: `scripts/index_template.html`(당시 파일명은
   `pipeline_index_template.html`) — WDS 토큰 재사용, 6개 섹션, Chart.js 미사용(순수
   CSS 바 차트)으로 안정성 확보, safeInit 방어 패턴 적용
5. **빌드 및 검증**: 빌드 스크립트 실행 → 파일 동기화 지연 이슈 발견(셸에서 직접
   재작성해 해결) → `node --check` 문법 검증 → jsdom 헤드리스 렌더링으로 6개 섹션
   전부·필터·nav 전환·마일스톤 토글 동작 확인
6. **as_of_date 표시 버그 수정**: 기준일 범위 표시에 괄호 부연설명이 섞여 나오는 문제
   발견 → YYYY-MM 접두 7자만 잘라 쓰도록 수정 후 재검증
7. **README/배포 준비**: 기존 oz-dashboard README에 신규 대시보드 섹션 추가, git 커밋
   시도 → `.git/index.lock` 잔여 파일 및 push 인증정보 부재로 이 환경에서는 커밋·푸시
   불가 확인 → 사용자가 로컬에서 직접 커밋·푸시하도록 안내
8. **신규 레포 분리**: 사용자가 처방-지급 대시보드와 무관한 별도 레포로 분리하기로
   결정 → `ai-drug-pipeline-dashboard/` 폴더에 필요한 파일만 재구성(스크립트 경로를
   `index.html`/`index_template.html` 기준으로 조정), 단독 README 작성, 기존
   oz-dashboard README는 처방-지급 대시보드 내용만 남도록 원복
   - 이 과정에서 관련 없는 예전 파일 3개가 실수로 함께 복사됨 → 연결 폴더의 파일
     삭제 제한으로 자동 정리 불가 → README에 "안 쓰는 파일"로 명시하고 사용자가
     직접 정리하도록 안내(교훈 5번 참고)

## 산출물 파일 목록

- `PRD_AI신약파이프라인_트래킹_대시보드.md` — 최신 PRD (v1.0)
- `index.html` — 최종 대시보드(단일 HTML, 배포 대상)
- `README.md` — 대시보드 단독 설명 문서
- `scripts/build_pipeline_dashboard.py` — CSV → JSON → HTML 생성 스크립트
- `scripts/index_template.html` — HTML/CSS/JS 템플릿
- `data/pipeline_data.json` — 정규화·집계된 데이터(= index.html에 임베드된 것과 동일)
- `source_data/ai_drug_pipeline_candidates.csv`, `drug_candidates_master.csv` — 원본 데이터
- `PROMPT_AI신약파이프라인_대시보드_재현.md` — 본 문서
