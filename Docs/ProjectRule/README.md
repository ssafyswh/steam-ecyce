# Team 08 Git Rule

## Branch 생성 원칙
### master
- 기본 branch. 프로젝트의 가장 최신 버전을 관리
### develop
- project 내부의 app 단위로 master branch에서 분기되는 branch
- 브랜치 이름은 devlop/app_name으로 작성 (ex. develop/libraries)
### feature
- devlop 브랜치에서 분기되어 앱 내에서 독립적으로 개발되는 기능들을 분리
- feature/기능으로 브랜치 생성 (ex. feature/login)
- 가급적 하나의 feature 브랜치에서는 하나의 기능만을 개발할 것


## Commit 제목 원칙
### 주의사항: 커밋 메시지의 제목은 영어로 작성함을 원칙으로 한다
1. 태그<br>
태그는 '[tag]'와 같이 작성한다.

| 타입 | 설명 |
|---|---|
| feat | 새로운 기능 추가 |
| add | 파일을 생성한 경우 |
| remove | 파일을 삭제만 한 경우 |
| fix | 버그 수정 |
| docs | 문서 수정 |
| style | 코드 스타일 변경 (코드 포매팅, 세미콜론 누락 등) 기능 수정이 없는 경우 |
| design | 사용자 UI 디자인 변경 (CSS 등) |
| test | 테스트 코드, 리팩토링 테스트 코드 추가 |
| refactor | 코드 리팩토링 |
| perf | 성능 개선 |
| chore | 빌드 업무 수정, 패키지 매니저 수정 (gitignore 수정 등) |
| rename | 파일 혹은 폴더명을 수정만 한 경우 |

2. 제목
- 태그와 제목은 띄어쓰기로 구분
- 첫 글자는 대문자로 작성
- 제목은 영문 기준 50글자 이하
- 명령문으로 작성
- 과거형으로 작성하지 않음
- 제목 끝에 마침표를 적지 않음

3. 본문
- 제목과 본문을 빈 행으로 구분
- 본문의 각 행은 영문 기준 72글자 이하

