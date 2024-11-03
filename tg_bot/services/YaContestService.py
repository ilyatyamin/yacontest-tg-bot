import json

import requests


class YaContestService:
    def __init__(self, yandex_token: str):
        self.__token = yandex_token
        self.__headers = {
            "Authorization": f"OAuth {yandex_token}"
        }

    def get_input_file(self,
                       id_contest: str,
                       id_submission: str,
                       test_id: str) -> str:
        # preprocessing
        if not id_contest.isdigit():
            raise NameError("Contest ID must be an integer.")
        if not id_submission.isdigit():
            raise NameError("Submission ID must be an integer.")
        if not test_id.isdigit():
            raise NameError("Test ID must be an integer.")
        test_id = str(int(test_id))

        is_get_normal_response = False
        global response

        for left_zero in range(0, 5):
            preprocessed_test_id = '0' * left_zero + test_id
            api_url = self.__get_input_file_url(id_contest, id_submission, preprocessed_test_id)

            response = requests.get(url=api_url,
                                    headers=self.__headers)
            if response.status_code == 200:
                is_get_normal_response = True
                break
        if not is_get_normal_response:
            raise Exception(
                json.loads(response.text)['message'] + "\nВозможно Вы указали неверные данные, проверьте Ваш запрос")
        else:
            return response.text

    def __get_input_file_url(self,
                             id_contest: str,
                             id_submission: str,
                             test_id: str):
        return f'https://api.contest.yandex.net/api/public/v2/contests/{id_contest}/submissions/{id_submission}/{test_id}/input'
