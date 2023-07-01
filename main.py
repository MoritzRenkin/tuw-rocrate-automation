from api_client import ApiClient

def main():
    client = ApiClient()
    records = client.get_all_records()
    print(records)


if __name__ == '__main__':
    main()
