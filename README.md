# Star Wars Genesis 비공식 한국어 가이드

[공식 Genesis 사이트](https://genesismodlist.com/)의 설치·업데이트·문제 해결 안내를 한국어 사용자에게 제공하는 커뮤니티 프로젝트입니다.

> Star Wars Genesis와 그 관계사에서 운영하거나 보증하는 사이트가 아닙니다. 원문과 내용이 충돌하면 **항상 원본 최신 가이드를 우선**합니다.

## 한국어 사이트

https://munument1.github.io/-KR-Starwars-Genesis/

## 완료한 페이지 (2026-10-07)

- [x] 홈 및 공통 메뉴
- [x] 신규 설치 **(1차 상세 번역 + 원본 스크린샷 연결)**
- [x] 설치 업데이트 **(1차 상세 번역 + 원본 스크린샷 연결)**
- [x] HD Overhaul **(상세 번역 + 원본 스크린샷 연결)**
- [x] 번역 정책
- [x] 문제 해결 목차
- [x] Self Help **(현재 원본 Yes/No 분기 전체 + TLDR/결과 페이지)**
- [x] Wabbajack Issues **(상세 번역)**
- [x] Mod Organizer Issues **(상세 번역)**
- [x] Ingame Issues **(상세 번역)**
- [x] Controller **(상세 번역 + 공식 바인드 이미지)** / Ultrawide / Linux
- [x] Incompatible Apps **(1차 요약본)**
- [x] Modifying Install **(1차 번역)**
- [x] General Performance / FPS Boosts / Menu Lag / Potato PC / Default Settings
- [x] F.A.Q. **(1차 번역)**
- [x] Patch Notes index + 8.8.31 상세 요약

## 남은 작업

- [x] Self Help 현재 질문/결과 페이지의 현지화·검수
- [x] 설치·업데이트 보조 절차의 핵심 안내 보완 (페이지 파일 / 루트 / 백신 / VC++ / MO2 / Documents / HD 업데이트)
- [x] HD Overhaul 상세 스크린샷/업데이트 예외 추가
- [x] 8.8.31 / 8.8.3 / 8.8.21 / 8.8.2 / 8.8.15 패치노트 번역
- [x] Wiki / Gameplay / Team / Volunteer / Credits **(1차 번역)**
- [x] Controls & Keybinds / Tips & Tricks / Quests / Lore / Difficulty
- [x] Beginner Guides / Donate **(1차 번역)**
- [x] 원문 업데이트 감지 자동화 — 원본 74페이지 매일 확인, 변경 시 GitHub Issue
- [x] Uninstall / Game Keys / Old Installer Migration / Downloads Cleaning **(1차 번역)**
- [x] Steam Auto Update / Modded Starfield Cleanup / Multiple Characters / Broken NPC / Modified Save
- [x] 자동 내부 링크·페이지 메타 검증 워크플로
- [ ] 실제 모바일 브라우저 시각 검수

## 원문 기준

2026-10-07 사이트 전체를 대조해 72개 한국어 페이지 중 66페이지에 핵심 정보 204개 항목과 참고 링크 174개를 보완했습니다. 기존 57페이지에 설치 보조 안내와 Wiki 자료 15페이지를 추가했습니다. 페이지별 원문 주소·본문 해시·검수 범위는 `content-coverage.json`에 기록합니다.

긴 원문은 사실 중심의 한국어 요약으로 보완하며, 모든 문장을 그대로 번역한 것은 아닙니다. 외부 자료 표와 영상은 원문에 연결하고 이미지·영상 내부의 영문까지 번역 완료했다고 주장하지 않습니다. 기존 번역과 한글 패치 적용 안내는 유지합니다.

- 최초 작업: 2026-10-07
- 최신 확인 패치노트: 8.8.31 (2026-09-28)
- 설치 안내 페이지: Genesis 8.8.3으로 표시
- 설치 및 업데이트 전 최신 Starfield 버전을 원문에서 재확인 필요

## 검색엔진

HTML에 `<meta name="robots" content="noindex,nofollow">`를 삽입했습니다. 저장소 안의 `robots.txt`는 GitHub 프로젝트 사이트에서 도메인 최상위 robots.txt가 아니므로 차단 효력을 보장하지 않습니다.

## 원칙

- 공식 페이지별 원문 주소와 확인 날짜 표시
- 명령어·폴더·파일명·모드명·오류 문구는 원문 표기 유지
- 설치 경로나 실행 순서를 임의로 만들지 않음
- 위험한 보안 설정 변경은 필요 최소한만 고려
- 사이트 가이드 번역과 게임 본편 번역은 별도

## 이미지 정책

원본 가이드의 스크린샷은 저장소에 복제하지 않고 `genesismodlist.com`이 호스팅하는 이미지 URL을 직접 참조합니다. 따라서 원본 이미지가 교체되거나 삭제되면 한국어판에서도 표시되지 않을 수 있습니다.

## 자동 검증

- `Check Genesis upstream`: 매일 원본 74페이지의 본문을 비교합니다. 변경이 감지되면 GitHub Issue를 생성/갱신합니다.
- `Validate Korean Genesis site`: HTML 변경 시 내부 링크, title, viewport 등을 자동 검사합니다.
- 원본 번역을 갱신한 뒤 변경 감지 기준값을 승인하려면 Actions → **Check Genesis upstream** → Run workflow에서 `accept_current=true`로 실행합니다.
