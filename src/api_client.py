import requests
import os
import json


prj_dir = os.path.dirname(__file__)
token_file_path = os.path.join(prj_dir, "api-access-token.txt")

class ApiClient:
    base_url = "https://test.researchdata.tuwien.ac.at/api/"

    def __init__(self):
        with open(token_file_path, "r") as token_file:
            self.__token: str = token_file.read()
            self.__token_suffix: str = f"?access_token={self.__token}"

    def build_url(self, rel_path:str):
        return self.base_url + rel_path.strip("/") + self.__token_suffix
    def get_all_records(self):
        url = self.build_url("records/")
        r = requests.get(url)
        return json.loads(r.text)
