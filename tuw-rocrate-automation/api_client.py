import requests
import json
import logging
from pathlib import Path

logger = logging.getLogger("ApiClient")
file_path = Path(__file__).parent.resolve()
token_file_path = file_path / "api-access-token.txt"


class APIResponseException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class InvenioRDMClient:
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
        if not r.ok:
            raise APIResponseException(f"Unexpected response code {r.status_code}, message body: {r.text}")
        return json.loads(r.text)

    def create_draft(self, draft_json: dict) -> str:
        """ Create a draft record without publishing.
        :param draft_json: Message Body according to InvenioRDM documentation.
        :return: ID of the draft record
        """
        url = self._build_url("records/")
        response = requests.post(url, json=draft_json)
        logger.debug(f"API Response to creating draft: {response.text}, draft_json:\n{draft_json}")
        if not response.ok:
            raise APIResponseException(f"Unexpected response code {response.status_code}, "
                                       f"message body: {response.text}")
        record_id = json.loads(response.text)["id"]
        return record_id

    def upload_draft_files(self, record_id: str, file_paths: list[Path] | list[str]):
        """
        TODO docu
        :param record_id: ID of the draft record
        :param file_paths:
        :return: None
        """
        file_paths: list[Path] = [Path(path) for path in file_paths]
        file_names: list[str] = [path.name for path in file_paths]

        # Create files on server
        create_url = self._build_url(f"records/{record_id}/draft/files")
        create_body = [{"key": filename} for filename in file_names]
        create_response = requests.post(create_url, json=create_body)
        logger.debug(f"API response to creating files: {create_response.text}")
        if not create_response.ok:
            raise APIResponseException(f"Unexpected response code {create_response.status_code}, "
                                       f"message body: {create_response.text}")

        for path in file_paths:
            # Upload binary data to files
            filename = path.name
            upload_url = self._build_url(f"records/{record_id}/draft/files/{filename}/content")
            upload_header = {"Content-Type": "application/octet-stream"}
            file_content = path.read_bytes()
            upload_response = requests.put(upload_url, headers=upload_header, data=file_content)
            logger.debug(f"API response to uploading file {path.resolve()}: {upload_response.text}")
            if not upload_response.ok:
                raise APIResponseException(f"Unexpected response code {upload_response.status_code},"
                                           f" message body: {upload_response.text}")

            # Commit file upload
            commit_url = self._build_url(f"records/{record_id}/draft/files/{filename}/commit")
            commit_response = requests.post(commit_url)
            logger.debug(f"API response to committing file upload {path.resolve()}: {commit_response.text}")
            if not commit_response.ok:
                raise APIResponseException(f"Unexpected response code {commit_response.status_code}, "
                                           f"message body: {commit_response.text}")

    def publish_draft(self, record_id: str):
        """
        TODO docu
        :param record_id: ID of the draft record
        :return: None
        """
        url = self._build_url(f"records/{record_id}/draft/actions/publish")
        response = requests.post(url)
        logger.debug(f"API response to publishing draft {record_id}: {response.text}")
        if not response.ok:
            raise APIResponseException(f"Unexpected response code {response.status_code}, "
                                       f"message body: {response.text}")