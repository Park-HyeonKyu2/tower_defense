# 맵 데이터 및 밸런스 도구

기존 GameMap, BalanceAnalyzer, Action 인터페이스와 JSON 키를 유지한다.
맵 좌표의 단위는 칸이며 경로는 칸 중심을 연결한다. 슬롯 경계는
(x, y, width, height), 슬롯 ID는 0~23이다. GameMap은 작업 디렉터리와
무관하게 data/map.json을 읽는다. 잘못된 데이터는 예외를 발생시키고
이미 로드한 맵은 보존한다.

## 실행

```sh
python scripts/balance.py --games 10 --stages 5 --output results/balance.json
python -m unittest discover -s tests -v
```

JSON에는 시드별 결과와 스테이지별 골드 변화 및 라이프 손실이 기록된다.
CSV에는 판별 요약이 기록된다. 오류가 있으면 종료 코드 1을 반환하며
오류 판은 클리어율에서 제외한다. 웨이브는 1/60초씩 최대 600초 진행한다.
구매 정책은 시드별 랜덤 정책이며 최적 플레이 가능성을 의미하지 않는다.

## 팀원 연결 사항

현재 engine.py의 _update_wave는 미구현이며 is_wave_complete 호출에
alive_enemies 인자가 누락되어 있다. 엔진 담당이 전투, 스폰, 정산을
연결해야 실제 밸런스 측정이 가능하다. 도구는 엔진 상태를 직접 변경하거나
전투 로직을 대신 구현하지 않는다.

stages.json은 기존 1~5 데이터를 유지하고 6~30은 기존
WaveManager._generate_wave 규칙을 명시했다. 현재 WaveManager는 JSON을
읽지 않는다. tower.py와 enemy.py도 자체 상수를 사용한다. 각 담당자가
데이터 로딩을 연결하기 전 JSON 수치 변경은 게임에 반영되지 않는다.
기획안과 다른 기존 수치는 팀 합의 없이 변경하지 않았다.
