from requests import get

def get_image_cat():
	url_request = 'https://api.thecatapi.com/v1/images/search'
	answer = get(url_request).json()
	return answer[0]["url"]