# PRD: AI 신약 파이프라인 경쟁사 트래킹 대시보드

| 항목 | 내용 |
|---|---|
| 작성자 | 박진영 (AI 신약개발 연구원) |
| 작성일 | 2026-07-13 |
| 상태 | Draft v1.0 |
| 대상 배포 | AI 신약개발 연구팀 (내부 보고/공유용) |

## 1. 배경 및 목적

인실리코 메디슨, 리커전 파마슈티컬스, 아이소모픽 랩스 등 "AI 네이티브" 신약개발 기업들의 파이프라인 진행 상황은 각사 뉴스룸·보도자료·학회 발표에 흩어져 있어, 연구팀이 경쟁 구도를 한눈에 파악하기 어렵다. 어떤 회사가 어떤 타겟·기전에서 얼마나 앞서 있는지, 자사가 검토 중인 타겟과 겹치는 경쟁사가 있는지를 확인하려면 매번 개별 기사를 찾아야 한다.

이 대시보드는 업로드된 경쟁사 파이프라인 데이터를 회사·타겟·개발단계 기준으로 정리해 경쟁 현황을 트래킹하는 것을 1차 목적으로 한다. 부가적으로, 공개 화합물 벤치마크 데이터(약물성·독성·효능 지표)를 참고 섹션으로 함께 제공해 자사 AI 후보물질 스크리닝 기준을 세울 때 참고할 수 있도록 한다.

## 2. 데이터 개요

업로드된 두 파일은 성격이 서로 다르며, **서로 연결(Join)할 공통 키가 없다.** 이 PRD 전체에서 두 파일은 독립된 두 섹션으로 다룬다.

**ai_drug_pipeline_candidates.csv** (경쟁사 파이프라인, 메인 데이터)
- 10행, 5개 기업의 후보물질: Insilico Medicine(4), Recursion Pharmaceuticals(3), Exscientia/Recursion 합병(1), Iambic Therapeutics(1), Isomorphic Labs(1)
- 컬럼: `company`, `candidate_name`, `target_mechanism`, `indication`, `ai_discovery_approach`, `current_stage`, `commercialized`, `key_milestone_note`, `source_url`, `as_of_date`
- 개발 단계 분포: Phase III(1), Phase I/II(3), Phase I(1), Early clinical Phase I/IIa(1), Phase I/Ib(1), 전임상/IND 준비(1), 중단·Discontinued(1)
- `commercialized`는 10건 전부 "No" — **AI 신약개발 후보물질 중 아직 상용화(승인)된 사례가 없다는 것이 핵심 시사점**
- `as_of_date`가 행마다 다름(2023-09 ~ 2026-07) — 데이터가 한 시점 스냅샷이 아니라 각 기사 발표 시점 기준임에 유의
- 각 행에 `source_url`(뉴스/보도자료 링크) 포함

**drug_candidates_master.csv** (화합물 벤치마크, 보조 데이터)
- 191행, 공개 ML 신약 벤치마크 4종 혼합: ClinTox(60), HIV(60), Tox21(59), BACE(12)
- 컬럼: `compound_id`, `source_dataset`, `input_smiles`, `canonical_smiles`, `mw`(분자량), `logp`, `hbd`, `hba`, `tpsa`, `rotatable_bonds`, `qed_druglikeness`, `lipinski_violations`, `toxicity_flag`, `toxicity_assay`, `fda_approved`, `developed_status`, `efficacy_assay`, `efficacy_value`, `efficacy_active_flag`
- `fda_approved` / `developed_status`: 1(승인, 57건) / 0(임상 독성 실패, 3건) / 빈값(131건, 원시 스크리닝 화합물로 미분류)
- `efficacy_value`는 데이터셋마다 형식이 다름 — BACE는 연속형 수치(pIC50), HIV는 범주형 텍스트(CI/CM) — **단순 합산·평균 시 형식이 섞이므로 주의**
- **이 화합물들은 file1의 경쟁사 후보물질이 아니라 공개 벤치마크 데이터셋의 화합물이며, 서로 매칭되지 않는다.** 대시보드에서는 "일반 참고 벤치마크"로만 취급한다.

## 3. 대상 사용자 및 사용 시나리오

**주 사용자:** 사내 AI 신약개발 연구팀 (경영진/타 부서 공유 시에도 동일 화면 사용)

**핵심 사용 시나리오**
1. 연구원이 자사가 검토 중인 타겟·기전(예: TNIK, USP1, MEK1/2 등)을 검색해 이미 경쟁사가 다루고 있는지 확인한다.
2. 회사별로 파이프라인 후보물질 수와 최고 진행 단계를 비교해 경쟁 구도를 파악한다.
3. 개발단계별 분포(전임상 → Phase I → Phase III → 중단)를 보고 업계 전반의 진행 속도와 상용화 사례 유무를 확인한다.
4. 최신 마일스톤을 시간순으로 훑어보고, 궁금한 항목은 `source_url`로 원문을 확인한다.
5. 화합물 벤치마크 섹션에서 승인 신약과 독성 실패 화합물의 물성 지표(QED, Lipinski 위반, logP 등) 분포를 참고해 자사 후보물질 스크리닝 기준을 세운다.
6. 전체 현황을 요약 카드로 캡처해 팀 내부 보고 자료로 활용한다.

## 4. 목표 및 성공 기준

| 목표 | 성공 기준 |
|---|---|
| 경쟁사 파이프라인 가시화 | 회사·타겟·개발단계 기준으로 10건의 후보물질을 필터링/정렬해 조회 가능 |
| 경쟁 구도 파악 지원 | 회사별 후보물질 수, 최고 진행단계, AI 플랫폼(Pharma.AI, Recursion OS 등)을 한 화면에서 비교 |
| 화합물 벤치마크 참고 제공 | 승인/독성실패 화합물 간 주요 물성 지표 분포 비교 가능 |
| 사용 편의성 | 별도 설치·서버·로그인 없이 파일 하나로 열람 가능 |
| 정확성 | 원본 CSV 값과 대시보드 표시값이 오차 없이 일치, 두 데이터셋이 연결되지 않는다는 점이 UI상 명확히 구분 |

## 5. 기능 요구사항 (핵심 뷰)

### 5.1 경쟁사 파이프라인 트래커 (메인 테이블)
- `company`, `candidate_name`, `target_mechanism`, `indication`, `ai_discovery_approach`, `current_stage`, `as_of_date`, `source_url`(링크)를 행 단위로 표시
- 필터: 회사, 개발단계, 기전/적응증 키워드 검색
- `key_milestone_note`는 행 확장(펼치기) 또는 상세 패널에서 전문 노출

### 5.2 개발단계 퍼널 뷰
- 전임상/IND 준비 → Phase I → Phase I/II → Phase III → (상용화) 순서의 퍼널 또는 막대 차트
- "중단(Discontinued)" 건은 퍼널과 별도로 구분 표시
- 상단에 "상용화 완료 후보물질: 0건" 인사이트를 명시적으로 강조

### 5.3 회사 간 비교 뷰
- 회사별 후보물질 수, 최고 진행단계, 대표 AI 플랫폼/접근법(Pharma.AI, Recursion OS, Centaur Chemist, AlphaFold 기반 엔진 등)을 카드 또는 비교 테이블로 제공

### 5.4 최신 마일스톤 피드
- `as_of_date` 내림차순 정렬 타임라인, `key_milestone_note` 요약과 `source_url` 링크 병기
- 데이터가 스냅샷이 아니라 기사 발표 시점 기준임을 안내 문구로 표기

### 5.5 화합물 벤치마크 (보조 섹션)
- `source_dataset`(ClinTox/HIV/Tox21/BACE)별 건수 요약
- 승인(`fda_approved=1`) vs 독성실패(`fda_approved=0`) vs 미분류 화합물 간 `qed_druglikeness`, `lipinski_violations`, `logp`, `tpsa` 등 분포 비교(박스플롯 또는 분포 차트)
- `toxicity_flag` 비율, 데이터셋별 `efficacy_assay` 요약(BACE 연속형 수치 / HIV 범주형 텍스트는 별도 표기, 혼합 집계 금지)
- 섹션 상단에 "아래는 공개 벤치마크 데이터이며 위 경쟁사 파이프라인과 직접 연결되지 않는 참고 자료입니다" 안내 배지 고정 노출

### 5.6 공통 요구사항
- 상단 요약 카드: 총 후보물질 수(10), 참여 기업 수(5), 최고 진행단계(Phase III), 상용화 완료 수(0), 데이터 기준 안내
- 전역 필터: 회사, 개발단계, 기전 검색
- 데이터 출처 신뢰도 안내: 각 행 `source_url` 명시, `as_of_date` 상이함을 고지하는 문구 상시 노출

## 6. 데이터 처리 요구사항

- **두 CSV는 조인하지 않는다.** 연결 키가 없으므로 완전히 독립된 두 섹션으로 다룬다.
- File1 `current_stage`는 값 표기가 혼재(영문/한글 혼용, 괄호 부연 설명 포함)하므로 정규화 매핑 테이블을 만들어 퍼널 단계로 그룹핑한다 (예: "Early clinical (Phase I/IIa)" → Phase I/II 그룹, "중단 (Discontinued)"→ 별도 상태값).
- File1 `commercialized`는 현재 전량 "No"이나, 향후 값이 바뀔 가능성을 고려해 하드코딩하지 않고 로직으로 판정한다.
- File2 `fda_approved`는 1/0/빈값 3분류로 처리한다 (1=승인, 0=임상 독성 실패, 빈값=미분류 원시 스크리닝 화합물). 빈값을 0으로 취급하지 않는다.
- File2 `efficacy_value`는 `source_dataset`에 따라 연속형(BACE, pIC50 수치)과 범주형(HIV, CI/CM 텍스트)이 혼재하므로, 집계·시각화 시 데이터셋별로 분리 처리한다.
- File2 `toxicity_assay`/`efficacy_assay`는 세미콜론(`;`)으로 구분된 다중값이 존재할 수 있어(예: `NR-AhR;SR-ARE;SR-MMP;SR-p53`), 필요 시 분해해 카운트한다.

## 7. 산출물 형식 및 기술 요구사항

- **형식:** 서버·로그인 없는 단일 HTML 파일 (기존 oz-dashboard 프로젝트와 동일한 패턴 — 인라인 `<style>`/`<script>`, Chart.js 등 CDN 활용, 빌드 스크립트로 데이터 임베딩)
- **데이터 갱신:** v1은 현재 업로드된 CSV 스냅샷 기준 1회성 정적 분석. 향후 새 경쟁사 소식이나 화합물 데이터가 추가되면 CSV에 행을 추가하고 재생성하는 구조를 권장
- **성능:** 데이터 규모가 작아(10행 + 191행) 브라우저 내 처리에 성능 이슈 없음

## 8. 범위 외 (Out of Scope, v1)

- 두 데이터셋 간 교차 조인/직접 비교 (연결 키 부재)
- 실시간 뉴스 크롤링 및 자동 업데이트 파이프라인
- 화합물 SMILES 구조의 2D/3D 시각화 렌더링
- 경쟁사 재무·투자(펀딩 라운드 등) 심층 분석
- 화합물 벤치마크(file2)를 실제 자사 파이프라인 후보물질과 매칭하는 기능 (현재 데이터상 연결 불가)

## 9. 리스크 및 제약사항

- File1은 10개 후보물질, 5개 기업으로 표본이 매우 작아 업계 전체 경쟁 구도를 대표하지 않는다는 점을 화면에 고지한다.
- File1의 `as_of_date`가 2023-09~2026-07로 넓게 분포해 있어, 회사별 "현재 상태"처럼 보이지만 실제로는 각기 다른 시점의 스냅샷임을 명확히 표기해야 한다.
- File2는 공개 ML 벤치마크(ClinTox/HIV/Tox21/BACE)이며 자사 실제 후보물질이 아니다. "우리 후보물질 현황"으로 오인되지 않도록 UI에서 시각적으로 명확히 구분한다(예: 별도 배경색, 안내 배지).
- `source_url`은 외부 뉴스/보도자료 링크로, 추후 링크 만료 가능성이 있다.

## 10. 다음 단계

1. 본 PRD 확정
2. 데이터 정규화 스크립트 작성(단계값 매핑, fda_approved 3분류 처리) 및 검증
3. 단일 HTML 대시보드 프로토타입 제작
4. 연구팀 리뷰 후 v1 배포
