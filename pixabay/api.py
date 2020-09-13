import requests
import time


def pixabay_api(url, api_key):
    api_key = '18254741-ce7f3e60a43d460c4e262ec4f'
    url = "https://pixabay.com/api/"
    query = 'lagos'
    PER_PAGE = 200

    PARAMS = {'q': query, 'per_page': PER_PAGE, 'page': 1}
    end_point = url + "?key" + api_key
    url_link = []
    req = requests.get(url=end_point, params=PARAMS)
    data = req.json()

    page_number = (data["totalHits"] // PER_PAGE) + 1

    for images in data["hits"]:
        url_link.append(images["webformatURL"])

    for page in range(2, page_number + 1):
        time.sleep(3)
        PARAMS["page"] = page
        req = requests.get(url=end_point, params=PARAMS)
        data = req.json()
        for images in data["hits"]:
            url_link.append(images["webformatURL"])

    index = 0
    for images in url_link:
        index += 1
        r = requests.get(images, allow_redirect=False)
        file_name = 'lagos_image' + str(index)
        return r
