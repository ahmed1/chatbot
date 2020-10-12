import json


def open_memo(filename):
    with open(filename, 'r') as f:  # technically just reading, but need to create if it doesn't yet exist
        memo = f.read().splitlines()
        return memo


def read_json(filename):
    with open(filename, 'r+') as f:
        opened_file = json.load(f)
    return opened_file


def write_db(restaurant_list):
    with open("./data/db/db.json", "w") as f:
        json.dump(restaurant_list, f, indent=2)


def main():
    restaurant_list = []
    biz_ids = open_memo("memo.txt")
    for biz in biz_ids:
        biz_json = read_json("./data/bid-" + biz + ".json") # all files are prepended with "bid-"
        restaurant_list.append(biz_json)
        # append_to_db_memo(biz_json["BusinessId"]) # maybe make a "written_to_database" memo table here
    write_db(restaurant_list)


if __name__ == '__main__':
    main()
