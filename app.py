from flask import Flask, request, jsonify
from func import crawling_lottecinema
from func import crawling_megabox
from func import crawling_cgv
from func import kofic_request
from func import ticketing
from func import util

app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def wekhook():
    # Dialogflow에서 보낸 요청 데이터 가져오기
    req = request.get_json(silent=True, force=True)

    # Dialogflow의 요청에서 필요한 정보 추출
    intent = req.get('queryResult').get('intent').get('displayName')
    user_query = req.get('queryResult').get('queryText')
    print(f"[DEBUG] - QUERY : ({intent}) {user_query}")

    try:
        # intent 이름에 따른 응답
        if intent == 'check_connection':
            response = {    # 복수 응답 테스트
                "fulfillmentMessages": [
                    {"text": {"text": ["연결 상태가 양호합니다."]}},
                    {"text": {"text": ["추가 테스트 메시지입니다."]}}
                ]
            }
        elif intent in ('Req Showtime - LotteCinema', 'Req Showtime - LotteCinema - AnotherBranch'):
            response = crawling_lottecinema.get_timetable(intent, req)
        elif intent in ('Req Showtime - CGV', 'Req Showtime - CGV - AnotherBranch'):
            response = crawling_cgv.get_timetable(intent, req)
        elif intent == 'Req Showtime - Megabox':
            response = crawling_megabox.get_timetable(intent, req)
        elif intent == 'get_movie_info':
            response = kofic_request.get_movie_info(req)
        elif intent == 'weekly_box_office_rank':
            response = kofic_request.get_weekly_boxoffice_rank()
        elif intent == 'recommend_movie':
            response = kofic_request.get_recommend_movie()
        elif intent == 'Ticketing':
            response = ticketing.get_ticketing_link(req)
        elif intent == 'Is Movie Now Theater':
            response = util.check_movie_showing(req)
        elif intent == 'Is Movie Now Theater - Req Showtime':
            response = util.get_movie_schedule(req)
        else:
            # intent가 매칭되지 않을 경우 기본 응답
            response = {"fulfillmentText": "요청하신 내용을 처리할 수 없습니다."}

        return jsonify(response)
    except Exception as e:
        print("[DEBUG] - ERROR : ", e)


if __name__ == '__main__':
    # 시작 전 CGV의 타임테이블 검사
    crawling_cgv.check_timetable()
    crawling_lottecinema.check_timetable()
    crawling_megabox.check_timetable()
    # 8080 포트에서 실행
    app.run(host='0.0.0.0', port=5050)
