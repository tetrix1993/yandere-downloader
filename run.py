from apputil import *
import json
import os
import requests

HTTP_HEADER = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
CONFIG_FILE = 'config.json'
LOGPATH = 'logpathfull'
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
            for i in ['base', 'pool', 'tag', 'user']:
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
                config[LOGPATH] = logpath + '/' + config['logpath']['download']
            else:
                config[LOGPATH] = None
        else:
            config[LOGPATH] = None

        if not 'download_type' in config:
            config['download_type'] = 'full'

        if 'max_pages' in config:
            if not isinstance(config['max_pages'], int):
                is_invalid = True
        else:
            config['max_pages'] = 5

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
            process_image()
        elif choice == 2:
            process_pool()
        elif choice == 3:
            process_tag()
        elif choice == 4:
            process_user()
        elif choice == 5:
            view_configs()
        elif choice != 0:
            print('[ERROR] Enter choices between 1 to 4. Enter 0 to exit program.')


def print_main_page_message():
    print('[INFO] Loading Main Screen...')
    print('Select option: ')
    print('1: Download by image ID')
    print('2: Download by pool ID')
    print('3: Download by tag')
    print('4: Download by user')
    print('5: View configuration settings')
    print('0: Quit program')


def process_image():
    print('[INFO] Option 1 selected - Download by image IDs')
    expr = input('Enter image IDs: ')
    image_ids = get_numbers_from_expression(expr)
    if len(image_ids) == 0:
        print('[ERROR] Invalid expression')
        return

    save_folders = config['save_folders']
    base_folder = save_folders['base']
    image_folder = save_folders['image']
    folder = '%s/%s' % (base_folder, image_folder)
    if not os.path.exists(folder):
        os.makedirs(folder)

    download_type = config['download_type']
    for image_id in image_ids:
        url = 'https://yande.re/post/show/' + str(image_id)
        try:
            soup = get_soup(url)
            if soup:
                image_url = None
                if download_type == 'sample':
                    meta_tag = soup.find('meta', {'property': 'og:image'})
                    if meta_tag and meta_tag.has_attr('content'):
                        image_url = meta_tag['content']
                else:
                    a_tag = soup.find('a', id='highres-show')
                    if a_tag and a_tag.has_attr('href'):
                        image_url = a_tag['href']
                if image_url:
                    download_image(image_url, folder + '/' + str(image_id), logpath=config[LOGPATH])
        except Exception as e:
            print('[ERROR] Error in processing image ID %s' % str(image_id))
            print(e)

    delete_empty_folders(folder)


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
                    image_id = post['id']
                    if download_type == 'sample' and 'sample_url' in post:
                        image_url = post['sample_url']
                    elif 'file_url' in post:
                        image_url = post['file_url']
                    else:
                        continue
                    if (first == 0 and last == 0) or first <= image_id <= last:
                        download_image(image_url, folder + '/' + str(image_id), logpath=config[LOGPATH])
    except Exception as e:
        print('[ERROR] Error in processing pool ID %s' % str(pool))
        print(e)

    delete_empty_folders(folder)


def process_tag():
    print('[INFO] Option 3 selected - Download by tag')
    tag = input('Enter tag name: ').strip()
    if ' ' in tag:
        print('[ERROR] Invalid tag name - Space is not allowed!')
        return

    if len(tag) == 0:
        return

    save_folders = config['save_folders']
    base_folder = save_folders['base']
    tag_folder = save_folders['tag']
    folder = '%s/%s/%s' % (base_folder, tag_folder, tag)
    if not os.path.exists(folder):
        os.makedirs(folder)
    process_search_page(tag, folder, is_tag=True)
    delete_empty_folders(folder)


def process_user():
    print('[INFO] Option 4 selected - Download by user name')
    user = input('Enter user name: ').strip()
    if ' ' in user:
        print('[ERROR] Invalid user name - Space is not allowed!')
        return

    if len(user) == 0:
        return

    save_folders = config['save_folders']
    base_folder = save_folders['base']
    user_folder = save_folders['user']
    folder = '%s/%s/%s' % (base_folder, user_folder, user)
    if not os.path.exists(folder):
        os.makedirs(folder)
    process_search_page('user%3A' + user, folder)
    delete_empty_folders(folder)


def process_search_page(tag, folder, is_tag=False):
    first, last = get_image_id_range(is_tag)
    if first is None or last is None:
        return
    if last == 0:
        last = 999999999
    for i in range(config['max_pages']):
        page = i + 1
        if is_tag:
            if page < first:
                continue
            if page > last:
                break
        page_url = 'https://yande.re/post?page=%s&tags=%s' % (str(page), tag)
        try:
            soup = get_soup(page_url)
            result = process_page(folder, first, last, soup, page_url, is_tag)
            if result != 0:
                break
            if not has_next_page(soup):
                break
        except Exception as e:
            print('[ERROR] Error in processing %s' % page_url)
            print(e)


def process_page(folder, first, last, soup, page_url, is_tag=False):
    try:
        lis = soup.find('div', class_='content').find_all('li')
        if len(lis) == 0:
            return 1
        first_id = int(lis[0]['id'][1:])
        last_id = int(lis[-1]['id'][1:])
        if is_tag or (last >= last_id and first <= first_id):
            for li in lis:
                id = int(li['id'][1:])
                if is_tag or (first <= id <= last):
                    image_url = li.find('a', class_='largeimg')['href']
                    download_image(image_url, folder + '/' + str(id))
        if first > last_id:
            return 1
    except Exception as e:
        print('[ERROR] Error in processing %s' % page_url)
        print(e)
        return -1
    return 0


def has_next_page(soup):
    paginator = soup.find('div', id='paginator')
    if paginator:
        pagination = paginator.find('div', class_='pagination')
        return pagination is not None
    return False


def get_image_id_range(is_tag=False):
    first = None
    last = None

    if is_tag:
        input_msg = 'Enter first page (enter 0 to download all): '
        input_msg_last = 'Enter last page: '
        invalid_msg = '[ERROR] Invalid page'
        validate_msg = '[ERROR] First page is greater than last page'
    else:
        input_msg = 'Enter first image ID (enter 0 to download all): '
        input_msg_last = 'Enter last image ID: '
        invalid_msg = '[ERROR] Invalid Image ID'
        validate_msg = '[ERROR] First image ID is greater than last image ID'

    try:
        first = int(input(input_msg).strip())
    except ValueError:
        print(invalid_msg)

    if first is not None:
        if first == 0:
            last = 0
        elif first < 0:
            print(invalid_msg)
            first = None
        else:
            try:
                last = int(input(input_msg_last).strip())
            except ValueError:
                print(invalid_msg)
            if last is not None and last < 0:
                print(invalid_msg)
                last = None
    if first is None or last is None:
        return None, None
    elif first > last:
        print(validate_msg)
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


def delete_all_empty_folders(base_folder):
    folders = os.listdir(base_folder)
    if len(folders) == 0:
        os.removedirs(base_folder)
        return
    for i in folders:
        folder = base_folder + '/' + i
        if os.path.isdir(folder):
            delete_all_empty_folders(folder)


def view_configs():
    print('[INFO] Here the save locations used to save the images. The configurations can be set in the file %s' % CONFIG_FILE)
    save_folders = config['save_folders']
    save_folder = save_folders['base'] + '/'
    print('Image Folder: %s' % (save_folder + save_folders['image']))
    print('Pool Folder: %s' % (save_folder + save_folders['pool']))
    print('Tag Folder: %s' % (save_folder + save_folders['tag']))
    print('User Folder: %s' % (save_folder + save_folders['user']))
    if config[LOGPATH]:
        print('Download Logs File: %s' % config[LOGPATH])
    input('[INFO] Press any key to continue...')


def close():
    global config
    if config is None:
        return
    if 'logpath' in config and 'base_folder' in config['logpath']:
        logpath = config['logpath']['base_folder'].strip()
        delete_empty_folders(logpath)
    base_folder = config['save_folders']['base']
    delete_all_empty_folders(base_folder)
    print('[INFO] Exiting program...')


if __name__ == '__main__':
    run()
