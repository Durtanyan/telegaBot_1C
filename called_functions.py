import requests
import shelve as sh
import json
from bs4 import BeautifulSoup
import config
import text_constants


# имя файла для модуля shelve
filename = "db_users"


# Просто вывводит картинку с кошаками при выполнении конманды /start
def get_image_cat():
    url_request = 'https://api.thecatapi.com/v1/images/search'
    answer = requests.get(url_request).json()
    return answer[0]["url"]


# Добавляет пользователя в БД. Срабатывает по команде /start
# Пользователь добавляется влюбом случае, права на работу с БД
# Ему добавляет администратор бота
def add_user_in_db(user_name, chat_id):
    f_db = sh.open(filename)
    if user_name in f_db.keys():
        return False
    if chat_id in text_constants.LIST_ID_ADMINISTRATOR:
        f_db[user_name] = [chat_id, [], True]
    else:
        f_db[user_name] = [chat_id, [], False]
    f_db.close()
    return True


# Изменяет список отчетов на которые подписан пользователь
# Список всегда перезаполняется заново.
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


# Очищает список отчетов по подписке
def unsubscribe_from_receiving_reports(user_name):
    f_db = sh.open(filename)
    if user_name in f_db.keys():
        list_data = f_db[user_name]
        empty_list = list()
        list_data[1] = empty_list
        f_db[user_name] = list_data
    return f_db[user_name]


# Выводит пользователю отчеты по подписке
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


# Подключается к api Allure Docker service UI, по лгину получает
# страницы по списку отчетов по подписке, парсит данные этой страницы и формирует
# общее сообщение пользователю. Используется в get_subscription_reports
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


# Получает имена отчетов по подписке для пользователя
def get_names_reports_available_user(list_subscription_reports):
    names_all_reports = text_constants.NAMES_TEST_PACKAGE
    list_available_reports = [names_all_reports[i - 1]
                              for i in list_subscription_reports]
    return list_available_reports


# Получает логин для подключения к api Allure Docker service UI
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


# Возвращает право пользователя на работу с БД.
# Пользование командами, подписка на отчеты и т.д.
def check_resolution(user_name):
    f_db = sh.open(filename)
    if user_name in f_db.keys():
        list_data = f_db[user_name]
        check_resolution = list_data[2]
        return check_resolution
    return False


# Команда администратора бота. Выводит данные о пользователях. Имя, id, право поьзоваться БД
def get_report_permissions(user_name):
    if check_resolution(user_name):
        f_db = sh.open(filename)
        result_txt = ""
        for key in list(f_db.keys()):
            result_txt += "---------------\n"
            result_txt += f'username: {key}, list reports: {f_db[key][1]} check: {f_db[key][2]}\n'
            result_txt += "---------------\n"
        return result_txt
    return 'Вы не админ бота.'


# Команда администратора бота. Добавляет пользователю право пользователя БД.
def add_view_reports(user_name):
    f_db = sh.open(filename)
    if user_name in f_db.keys():
        list_data = f_db[user_name]
        list_data[2] = True
        f_db[user_name] = list_data
        f_db.close()
        return True
    return False


# Удаляет у пользователя права на доступ к БД.
def delete_view_reports(user_name):
    f_db = sh.open(filename)
    if user_name in f_db.keys():
        list_data = f_db[user_name]
        list_data[2] = False
        f_db[user_name] = list_data
        f_db.close()
        return True
    return False


# Выдает по запросу chat_id пользователя из БД
def get_user_id(user_name):
    f_db = sh.open(filename)
    if user_name in f_db.keys():
        list_data = f_db[user_name]
        return list_data[0]


# get_report_permissions("Durtanyan")
# unsubscribe_from_receiving_reports("Durtanyan")
# add_user_in_db("Durtanyan_1", 1262060646)
# add_user_in_db("Durtanyan_2", 1262060647)
# add_user_in_db("Durtanyan_3", 1262060648)
# add_user_in_db("Durtanyan_4", 1262060649)
# delete_view_reports("Durtanyan_2")
