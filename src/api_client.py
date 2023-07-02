import requests
import json
import logging
from pathlib import Path

logger = logging.getLogger("ApiClient")
prj_dir = Path(__file__).parent.resolve()
token_file_path = prj_dir / "api-access-token.txt"

class ApiClient:
    base_url = "https://test.researchdata.tuwien.ac.at/api/"

    def __init__(self):
        with open(token_file_path, "r") as token_file:
            self.__token: str = token_file.read()
            self.__token_suffix: str = f"?access_token={self.__token}"

    def _build_url(self, rel_path:str) -> str:
        return self.base_url + rel_path.strip("/") + self.__token_suffix

    def get_all_records(self) -> dict:
        url = self._build_url("records/")
        r = requests.get(url)
        return json.loads(r.text)

    def create_draft(self, draft_json: dict) -> str:
        """
        Create a draft record without publishing.

        :param draft_json: Message Body according to InvenioRDM documentation.
        :return: ID of the draft record
        """
        logger.debug("Creating draft record.")
        url = self._build_url("records/")
        response = requests.post(url, json=draft_json)
        logger.debug(f"API Response body: {response.text}")
        record_id = json.loads(response.text)["id"]
        return record_id

    def upload_draft_files(self, record_id: str, file_paths: list[Path]):
        """
        TODO docu
        :param record_id: ID of the draft record
        :param file_paths:
        :return:
        """

        # Create files on server
        create_url = self._build_url(f"records/{record_id}/draft/files")

        file_paths: list[Path] = [Path(path) for path in file_paths]
        file_names: list[str] = [path.name for path in file_paths]

        create_body = [{"key": filename} for filename in file_names]
        create_response = requests.post(create_url, json=create_body)


        for path in file_paths:
            # Upload binary data to files
            filename = path.name
            upload_url = self._build_url(f"records/{record_id}/draft/files/{filename}/content")
            upload_header = {"Content-Type": "application/octet-stream"}
            file_content = path.read_bytes()
            upload_response = requests.put(upload_url, headers=upload_header, data=file_content)

            # Commit file upload
            commit_url = self._build_url(f"records/{record_id}/draft/files/{filename}/commit")
            commit_response = requests.post(commit_url)
            pass

    def publish_draft(self, record_id: str):
        """
        TODO docu
        :param record_id: ID of the draft record
        :return:
        """
        logger.debug("Publishing draft record.")
        url = self._build_url(f"records/{record_id}/draft/actions/publish")
        response = requests.post(url)
        print(response)