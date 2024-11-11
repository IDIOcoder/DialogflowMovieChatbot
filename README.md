# 영화정보제공 챗봇 웹훅 서버

### 설명
학교 과제로 진행된 Dialogflow를 이용한 챗봇 제작 과제로, Dialogflow의 Webhook사용을 위해 작성한 Flask 서버 코드입니다.
KOFIC API와 크롤링을 이용하여 간단한 영화 정보와, 박스오피스 순위를 제공합니다.
  - 사용자가 특정영화에 대한 정보를 요청하면, DB에 등록된 영화의 정보를 가져와 제공합니다.
  - '요즘 영화 볼거 뭐있지?' 혹은 '영화 추천해줘' 등의 질문에 DB에 등록된 주간 박스오피스 순위를 기준으로 응답합니다.
크롤링을 통해 서울권 CGV, 롯데시네마, 메가박스의 상영 스케줄 정보를 저장하여 사용합니다.
  - 롯데시네마와 메가박스의 경우 request를 통해 정보를 받아오며, CGV의 경우 selenium을 통한 크롤링으로 정보를 가져옵니다.
  - 받아온 정보는 json파일에 저장되며, 실제 응답에서 해당 json파일을 사용합니다.

### 사용방법
- 로컬환경에서 구동하는 것을 기준으로 작성되었습니다.
- .env파일에 KOFIC_KEY로 API키를 작성하거나, 코드내에 키를 작성해야 KOFIC API관련 기능들을 사용할 수 있습니다.
- CGV는 selenium을 통해 크롤링됩니다. headless옵션이 활성화 되어있지 않으므로, Chrome이 필요합니다.
- 상영관 코드는 포함되어있지 않습니다. 코드 실행시 상영관 코드를 저장한 json파일이 필요합니다.

### 개선해야할 점
- 코드 개선
- Dialogflow 의 intent를 수정하여 더 자연스럽게 작동할 수 있도록 수정
  - 현재 각 영화관에 대해 intent가 설정되어 있는데, intent를 하나로 통합하고, 입력된 영화관/지점 정보를 유연하게 가져올 수 있도록 개선
  - 각 intent별로 추가적으로 발생할 수 있는 시나리오에 대한 추가적인 기능 개발
- 당일의 상영 스케줄뿐만아니라 다른 날의 상영 스케줄도 활용할 수 있도록 개선
