from apputil import get_soup
import json
import os
import argparse


USER_PAGE_PREFIX = 'https://yande.re/post?tags=user%3A'
CONFIG_FILE = 'config.json'


def run(username):
    global config
    config = read_config_file()
    if config is not None:
        save_folders = config['save_folders']
        base_folder = save_folders['base']
        update_folder = save_folders['update']
        output_folder = f'{base_folder}/{update_folder}'
        output_filepath = f'{output_folder}/{username}.txt'
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        last_id = 'None'
        if os.path.exists(output_filepath):
            with open(output_filepath, 'r', encoding='utf-8') as f:
                last_id = f.read().strip()

        url = USER_PAGE_PREFIX + username
        try:
            soup = get_soup(url)
            lis = soup.select('#post-list-posts li')
            if len(lis) > 0:
                id_ = lis[0].get('id')
                if len(id_) > 1:
                    new_id = id_[1:]
                    if new_id != last_id:
                        print(f'[Yandere] User "{username}" has uploaded new image(s). (Current: "{new_id}", Previous: "{last_id}")')
                        with open(output_filepath, 'w+', encoding='utf-8') as f:
                            f.write(new_id)
        except Exception as e:
            print(e)


def read_config_file():
    global config
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, encoding='utf-8') as f:
            config = json.load(f)
        is_invalid = False
        if 'save_folders' in config:
            for i in ['update']:
                if i not in config['save_folders']:
                    is_invalid = True
                    break
        else:
            is_invalid = True

        if is_invalid:
            print("[ERROR] The configuration file %s is invalid." % CONFIG_FILE)
            config = None
        return config
    else:
        print("[ERROR] The configuration file %s is not found." % CONFIG_FILE)
        return None


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('U', help='username')
    args = parser.parse_args()
    run(args.U)
