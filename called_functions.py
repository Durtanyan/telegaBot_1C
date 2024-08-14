from requests import get
import shelve as sh


filename = "db_users"


def get_image_cat():
    url_request = 'https://api.thecatapi.com/v1/images/search'
    answer = get(url_request).json()
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
