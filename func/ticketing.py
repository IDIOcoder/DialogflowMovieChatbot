from datetime import datetime
from func import crawling_lottecinema
from func import crawling_megabox
from func import crawling_cgv


def get_response(url):
    response = ("해당 영화관 로그인이 필요한 서비스입니다. 예매 링크를 제공해 드릴게요!\n"
                f"{url}")
    print(url)
    return {"fulfillmentText": response}


def get_ticketing_link(request):
    output_contexts = request.get('queryResult').get('outputContexts', [])

    # outputContexts가 없는 경우 영화관 선택을 유도하는 메시지 반환
    if not output_contexts:
        return {"fulfillmentText": "어떤 영화관에서 예매 하시겠어요?"}

    # outputContexts가 존재할 경우
    parameters = {}
    for context in output_contexts:
        parameters.update(context.get('parameters', {}))

    # theater와 branch 추출
    theater = parameters.get('theater')
    branch = None

    # branch-로 시작하는 파라미터 찾기
    for key, value in parameters.items():
        if 'branch' in key.lower():
            branch = value
            break

    # branch 값이 없거나 '점'으로 끝나는 경우 '점' 제거
    if branch and branch[-1] == '점':
        branch = branch[:-1]

    # 예매 링크 생성
    if theater == "CGV":
        return get_cgv_ticketing_link(branch)
    elif theater == "롯데시네마":
        return get_lottecinema_link(branch)
    elif theater == "메가박스":
        return get_megabox_link(branch)
    else:
        return {"fulfillmentText": "요청하신 영화관을 찾을 수 없습니다."}


def get_cgv_ticketing_link(branch):
    date = datetime.today().strftime("%Y%m%d")
    cinema_id = crawling_cgv.get_code(branch)
    if cinema_id:
        url = f"http://www.cgv.co.kr/theaters/?areacode=01&theaterCode={cinema_id}&date={date}"
        return get_response(url)
    else:
        return {"fulfillmentText": "해당 지점을 찾을 수 없습니다."}


def get_lottecinema_link(branch):
    cinema_id = crawling_lottecinema.get_code(branch)
    if cinema_id:
        url = f"https://www.lottecinema.co.kr/NLCHS/Cinema/Detail?divisionCode=1&detailDivisionCode=1&cinemaID={cinema_id}"
        return get_response(url)
    else:
        return {"fulfillmentText": "해당 지점을 찾을 수 없습니다."}


def get_megabox_link(branch):
    cinema_id = crawling_megabox.get_code(branch)
    if cinema_id:
        url = f"https://megabox.co.kr/theater?brchNo={cinema_id}"
        return get_response(url)
    else:
        return {"fulfillmentText": "해당 지점을 찾을 수 없습니다."}
