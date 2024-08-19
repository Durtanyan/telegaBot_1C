import requests
import shelve as sh
import json
from bs4 import BeautifulSoup
import config
import text_constants


filename = "db_users"


def get_image_cat():
    url_request = 'https://api.thecatapi.com/v1/images/search'
    answer = requests.get(url_request).json()
    return answer[0]["url"]


def add_user_in_db(user_name, chat_id):
    f_db = sh.open(filename)
    if user_name in f_db.keys():
        return False
    f_db[user_name] = [chat_id, []]
    f_db.close()
    return True


def add_reports_to_subscription(user_name, list_reports):
    f_db = sh.open(filename)
    if user_name in f_db.keys():
        list_data = f_db[user_name]
        # Каждый раз перезаполняем список отчетов по подписке заново.
        copy_list = list()
        [copy_list.append(i) for i in list_reports]
        list_data[1] = copy_list
        f_db[user_name] = list_data
    f_db.close()


def unsubscribe_from_receiving_reports(user_name):
    f_db = sh.open(filename)
    if user_name in f_db.keys():
        list_data = f_db[user_name]
        empty_list = list()
        list_data[1] = empty_list
        f_db[user_name] = list_data
    # f_db.close()
    return f_db[user_name]


def get_subscription_reports(user_name):
    f_db = sh.open(filename)
    if user_name in f_db.keys():
        list_data = f_db[user_name]
        chat_id = list_data[0]
        list_subscription_reports = list_data[1]
        if len(list_subscription_reports) != 0:
            login_allire_docker_service_ui = get_login_allure_docker_service_ui()
            names_reports_available_user = get_names_reports_available_user(
                list_subscription_reports)
            text_message_user = get_text_message_user(
                login_allire_docker_service_ui, names_reports_available_user)

            return text_message_user
        return "У вас нет отчетов по подписке."


def get_text_message_user(login_allire_docker_service_ui, names_reports_available_user):
    cookies = {"access_token_cookie": login_allire_docker_service_ui}
    final_text = ""
    for name in names_reports_available_user:
        data_reports = requests.get(
            f"http://192.168.23.148:5050/allure-docker-service/projects/{name}", cookies=cookies)
        index_latest_report = json.loads(data_reports.text)[
            "data"]["project"]["reports_id"][1]

        data = requests.get(
            f"http://192.168.23.148:5050/allure-docker-service/emailable-report/export?project_id={name}", cookies=cookies)
        html = data.text
        soup = BeautifulSoup(html, 'html.parser')
        page_title = soup.find('div', class_='table-responsive')
        thead = page_title.find("thead")
        tbody = page_title.find("tbody")
        th_head = thead.find_all("th")
        th_tbody = tbody.find_all("th")
        count = 0
        message = "__________" + "\n" + \
            f"{name} № {index_latest_report}:\n"
        for i in thead.find_all("th"):
            count += 1
        for i in range(count):
            message += th_head[i].text + " = " + th_tbody[i].text + "\n"
        message += "__________\n"
        final_text += message
    return final_text


def get_names_reports_available_user(list_subscription_reports):
    names_all_reports = text_constants.NAMES_TEST_PACKAGE
    list_available_reports = [names_all_reports[i - 1]
                              for i in list_subscription_reports]
    return list_available_reports


def get_login_allure_docker_service_ui():
    query = {
        "username": config.USERMANE_ALLUREDOCKERSERVUCE,
        "password": config.PASSWORD_ALLUREDOCKERSEVICE
    }
    headers = {'content-type': 'application/json', "accept": "*/*"}
    url = "http://192.168.23.148:5050/allure-docker-service/login"
    try:
        res = requests.session().request("POST",
                                         url=url, json=query, headers=headers, timeout=10)
        if res.status_code == 200:
            answer = res.text
            login = json.loads(answer)["data"]["access_token"]
            return login
    except requests.exceptions.RequestException as e:
        return e
