# AI 빌더스랩 · 현장 실습 교실

AI를 처음 쓰는 일반인을 위한 오프라인 교육 사이트입니다. 설치·파일 관리부터 도움이 필요한 학습자를 기준으로, 강사 시연 → 함께 실행 → 새 자료로 독립 수행 → 피드백을 구성했습니다.

공개 주소: https://aihubos.github.io/builderslab-curriculum/

## 사용 안내

- 수강생 공유: handouts.html — 과정별 3쪽, 전체 18쪽 PDF와 수정 가능한 Markdown. 강사 메모·모범 답안 없음.
- 상세 교재: lessons.html — 6개 과정·53개 기본 실습 단계, Windows/Mac 안내, 샘플·요청문·완료 기록.
- 강사 자료실: teaching.html — 6개 진행안, 102장 웹 슬라이드, 편집 가능한 PPTX, 강사 운영 PDF.
- 과정별 게임: missions.html — 6개 보스·36개 상황 미션. 각 교재의 독립 과제 뒤에서 시작합니다.
- 준비 안내: ready.html — 사전 준비와 출발점 점검.
- 실습 과제: 각 교재의 독립 과제와 4항목 평가표, 세 단계 힌트, 모범 확인 기준, 복습 기록지.

첫걸음·업무·지식·홈페이지 과정은 권장 150분, Hermes·작은 앱은 권장 180분으로 설계했습니다. 휴식 포함, 설치 준비 시간은 별도입니다. 실제 개설 일정·기간·정원·수강료를 확정한 공지가 아닙니다.

## 실행과 수정

정적 사이트 생성에는 Python 표준 라이브러리만 필요합니다.

~~~sh
python3 build.py
python3 check.py
python3 -m http.server 4187 --bind 127.0.0.1
~~~

교육 원문을 변경했다면 문서도 다시 생성합니다. 문서 생성에는 reportlab, python-pptx, LibreOffice(soffice)가 필요합니다. 새로운 의존성을 사이트 방문자가 설치할 필요는 없습니다.

~~~sh
python3 export_materials.py
python3 build.py
python3 check.py
~~~

문서용 한글 글꼴 기본값은 macOS AppleGothic입니다. 다른 환경에서는 CLASSROOM_FONT에 한글을 포함한 TrueType 파일 경로를 지정합니다. PPTX에는 맑은 고딕을 지정하며, macOS LibreOffice 변환 시 시스템 한글 글꼴을 사용하도록 설정합니다. PDF는 글꼴이 포함된 배포본입니다. 생성된 파일은 assets/teaching에 있습니다.

## 원본과 생성물

- courses.json: 과정 소개·목차·선행 조건·결과물.
- lesson-content.html: 첫걸음 7단계 원문.
- workbooks.json: 다른 5개 과정의 46단계 원문.
- missions.json: 과정별 게임 문제·힌트·해설·복습 위치.
- missions.py 및 assets/league: 게임 페이지 생성, 상태 처리, 카드 배틀 화면.
- teaching.json: 목표·핵심 개념·현장 시간표·강사 발문·새 과제·평가표·복습.
- build.py, workbooks.py, teaching.py: 30개 교육 웹페이지와 다운로드 묶음 생성.
- export_materials.py: 상세 PDF 6개, 요약 PDF 6개와 합본, 강사 운영안, PPTX 6개와 슬라이드 PDF 생성.
- assets/practice: 직접 작성한 가상 샘플, 비교 자료, 홈페이지·할 일 앱 완성 예제.
- assets/previews: 직접 작성한 교육용 결과 예시.
- assets/downloads: 과정별 실습 묶음. ZIP 루트의 challenge.txt가 독립 과제 입력입니다.
- assets/teaching/student-handouts.zip: 수강생 요약 전용 공유 묶음.
- assets/teaching/classroom-kit.zip: 강사 전체 자료 묶음. 정답·강사 메모 포함.
- check.py: 생성 페이지·연결·53단계·과제·시간표 합계·슬라이드 메모·ZIP 최신 파일 검증.

외부 강의의 이전 참고 영상은 사이트에서 제거하고 로컬 참고자료 폴더에 보관했습니다. 참고 원본 자료와 output 검증 이미지는 GitHub에 올리지 않습니다. 로고는 사용자가 제공한 원본입니다.

## 운영 범위

페이지 자체에서 AI를 실행하거나 결제·등록·수강생 정보를 수집하지 않습니다. GitHub Pages의 main 브랜치 루트에서 배포합니다. 모든 웹 자료와 링크는 공개 자료이며, 강사 자료실도 접근 제한 기능이 없습니다.

완료 기록은 현재 브라우저의 과정별 키에 저장됩니다. 첫걸음은 builderslab-codex-lesson-v1, 다른 과정은 builderslab-과정-lesson-v1입니다. 초기화는 해당 과정의 체크만 지웁니다. 준비 점검의 체크는 저장하지 않습니다.

Hermes는 개인 컴퓨터 설치와 기존 ChatGPT/Codex 구독 인증 기준입니다. OpenAI와 Hermes 공식 안내를 2026-09-22 확인했습니다. 공식 출처는 각 교재에 있습니다. 지원 기기와 계정 접근, 수강생별 실제 설치·인증은 수업 전에 강사가 확인해야 합니다.

샘플·과제·목표·평가표는 자체 작성했습니다. 웹·앱 완성 예제와 인쇄·슬라이드 파일을 직접 확인했고, AI 모델의 출력 문장이 매번 동일함을 보장하지 않습니다. 강사는 제공된 진행안으로 수업 전 리허설을 합니다.

## 과정 마무리 게임

각 과정 소개·실습 교재·수강생 요약본·강의 마지막 슬라이드에서 해당 게임으로 이동합니다. 기본 5개와 보스 1개를 모두 해결하면 배지를 얻습니다. 오답은 해설 뒤 대기열 끝으로 돌아오고, 힌트를 사용할 수 있습니다. 시간 제한이나 탈락은 없습니다.

첫 시도 정답 20 XP, 힌트·재도전 정답 10 XP, 클리어 보너스 80 XP입니다. 재연습할 때 최고 기록만 유지하며 반복 횟수로 XP를 추가하지 않습니다. 게임은 먼저 연습할 수 있고, 교재에서 실습 체크와 게임 클리어를 모두 마쳤을 때 과정 마무리로 표시합니다. 실제 파일과 독립 수행 여부는 강사가 함께 확인합니다.

진행 중인 질문·해설·오답·배지는 현재 브라우저의 builderslab-course-game-v1-과정 키에 저장합니다. 기록을 읽지 못하면 기존 값을 보존하고 현재 화면에서 플레이합니다. 기록 초기화는 해당 과정 게임에만 적용하며, 실습 체크와 다른 과정은 건드리지 않습니다. 클리어 기록은 텍스트로 내려받습니다.

원작: https://jeremy.ai-hub-os.com/textbooks/games/builders-league/ — 사용자의 카드 배틀·성장·복습 흐름과 픽셀 몬스터 함수를 재사용하고, 현재 6개 과정에 맞춘 문제·진행 방식·화면을 새로 구성했습니다. 원작 사이트의 경험치와 별도로 기록합니다. 기존 원작 파일은 수정하지 않았습니다.

게임 동작 확인: node check-missions.mjs (python3 check.py에도 포함).
