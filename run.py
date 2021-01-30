from apputil import download_image, get_soup
import json
import os
import requests

HTTP_HEADER = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
CONFIG_FILE = 'config.json'
config = {}


def run():
    global config
    print('[INFO] Starting up Yandere Downloader...')
    config = read_config_file()
    if config is not None:
        execute_main_page()
    close()


def read_config_file():
    global config
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, encoding='utf-8') as f:
            config = json.load(f)
        is_invalid = False
        if 'save_folders' in config:
            for i in ['base', 'artist', 'pool', 'tag', 'user']:
                if i not in config['save_folders']:
                    is_invalid = True
                    break
        else:
            is_invalid = True

        if 'logpath' in config and 'base_folder' in config['logpath']:
            logpath = config['logpath']['base_folder'].strip()
            if not os.path.exists(logpath):
                os.makedirs(logpath)
            if 'download' in config['logpath']:
                config['logpathfull'] = logpath + '/' + config['logpath']['download']
            else:
                config['logpathfull'] = None
        else:
            config['logpathfull'] = None

        if not 'download_type' in config:
            config['download_type'] = 'full'

        if is_invalid:
            print("[ERROR] The configuration file %s is invalid." % CONFIG_FILE)
            config = None
        return config
    else:
        print("[ERROR] The configuration file %s is not found." % CONFIG_FILE)
        return None


def execute_main_page():
    choice = -1
    while choice != 0:
        print_main_page_message()
        try:
            choice = int(input("Enter choice: ").strip())
        except:
            print('[ERROR] Invalid choice.')
            continue

        if choice == 1:
            process_artist()
        elif choice == 2:
            process_pool()
        elif choice == 3:
            print('By tag')
        elif choice == 4:
            print('By user')
        elif choice != 0:
            print('[ERROR] Enter choices between 1 to 4. Enter 0 to exit program.')


def print_main_page_message():
    print('[INFO] Loading Main Screen...')
    print('Select option to download: ')
    print('1: By artist name')
    print('2: By pool ID')
    print('3: By tag name')
    print('4: By user name')
    print('0: Quit program')


def process_artist():
    print('[INFO] Option 1 selected - Download by artist name')
    artist = input('Enter artist name: ').strip()
    if ' ' in artist:
        print('[ERROR] Invalid artist name - Space is not allowed!')
        return


def process_pool():
    global config
    print('[INFO] Option 2 selected - Download by pool ID')
    try:
        pool = int(input('Enter pool ID: ').strip())
    except ValueError:
        print('[ERROR] Invalid Pool ID')
        return

    if pool <= 0:
        print('[ERROR] Invalid Pool ID')
        return

    first, last = get_image_id_range()
    if first is None or last is None:
        return

    save_folders = config['save_folders']
    base_folder = save_folders['base']
    pool_folder = save_folders['pool']
    folder = '%s/%s/%s' % (base_folder, pool_folder, str(pool))
    if not os.path.exists(folder):
        os.makedirs(folder)

    url = 'https://yande.re/pool/show/%s' % str(pool)
    try:
        result = requests.get(url, headers=HTTP_HEADER)
        result.raise_for_status()
        json_str = result.content.decode().split('Post.register_resp(')[1].split(');')[0]
        output = json.loads(json_str)
        download_type = config['download_type']
        if 'posts' in output:
            for post in output['posts']:
                if 'id' in post:
                    pool_id = post['id']
                    if download_type == 'sample' and 'sample_url' in post:
                        image_url = post['sample_url']
                    elif 'file_url' in post:
                        image_url = post['file_url']
                    else:
                        continue
                    if (first == 0 and last == 0) or first <= pool_id <= last:
                        download_image(image_url, folder + '/' + str(pool_id), logpath=config['logpathfull'])
    except Exception as e:
        print('[ERROR] Error in processing pool ID %s' % str(pool))
        print(e)

    delete_empty_folders(folder)


def get_image_id_range():
    first = None
    last = None

    try:
        first = int(input('Enter first image ID (enter 0 to download all): ').strip())
    except ValueError:
        print('[ERROR] Invalid Image ID')

    if first is not None:
        if first == 0:
            last = 0
        elif first < 0:
            print('[ERROR] Invalid Image ID')
            first = None
        else:
            try:
                last = int(input('Enter last image ID: ').strip())
            except ValueError:
                print('[ERROR] Invalid Image ID')
            if last is not None and last < 0:
                print('[ERROR] Invalid Image ID')
                last = None
    if first is None or last is None:
        return None, None
    elif first > last:
        print('[ERROR] First image ID is greater than last image ID')
        return None, None
    return first, last


def delete_empty_folders(filepath):
    split1 = filepath.split('/')
    for i in reversed(range(len(split1))):
        path = ''
        for j in range(i + 1):
            path += split1[j]
            if j != i:
                path += '/'
        if os.path.exists(path) and len(os.listdir(path)) == 0:
            os.removedirs(path)


def close():
    global config
    if 'logpath' in config and 'base_folder' in config['logpath']:
        logpath = config['logpath']['base_folder'].strip()
        delete_empty_folders(logpath)
    print('[INFO] Exiting program...')


if __name__ == '__main__':
    run()
