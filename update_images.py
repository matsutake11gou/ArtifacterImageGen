import math
import os
import requests
from json import dumps, loads
from io import BytesIO
from PIL import Image


cwd = os.path.abspath(os.path.dirname(__file__))

CHARA_DIR = os.path.join(
    cwd, 'character'
)
WEAPON_DIR = os.path.join(
    # 'test_images', 'weapons'
    cwd, 'weapon'
)
ARTIFACT_DIR = os.path.join(
    # 'test_images', 'artifact'
    cwd, 'Artifact'
)


# 現在の情報を取得
def load_update_list():
    file_path = os.path.join(cwd, 'update_list.json')
    result = dict(
        characters=dict(),
        weapons=dict(),
        artifacts=dict(),
    )
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = f.read()
        result = loads(data)
    except FileNotFoundError:
        print('update_listが存在しません。')
    return result


# 更新後の情報を保存
def save_update_list(update_list):
    file_path = os.path.join(cwd, 'update_list.json')
    with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(dumps(update_list, indent=2, ensure_ascii=False))


# 画像保存
def save_image(img_url, out_path):
    try:
        content = requests.get(img_url).content
        binary = BytesIO(content)
        image = Image.open(binary)
        image.save(out_path)
        return True
    except:
        print(
            '画像保存に失敗しました。'
            f' {img_url=}'
        )
        return False


# 立ち絵保存
def save_avatar_image(img_url, out_path: str, size=(2048, 1024)):
    try:
        content = requests.get(img_url).content
        binary = BytesIO(content)
        image = Image.open(binary)
        canvas = Image.new('RGBA', size=size, color=(0, 0, 0, 0))
        scale = min(canvas.width/image.width, canvas.height/image.height)
        resized_image = image.resize(size=(int(image.width*scale), int(image.height*scale)))
        point = (
            int(canvas.width/2 - resized_image.width/2),
            int(canvas.height/2 - resized_image.height/2),
        )
        print('paste')
        canvas.paste(resized_image, point)
        print('save')
        canvas.save(out_path)
        return True
    except Exception as e:
        print(e)
        print(
            'キャラクターの立ち絵画像保存に失敗しました。'
            f' {img_url=}'
        )
        return False


# HoYoWikiのAPIを叩いて
# キャラ・武器・聖遺物の一覧を取得する
# menu_id
# キャラ一覧: 2
# 武器一覧: 4
# 聖遺物: 5
def __request_page_list(menu_id):
    url = 'https://sg-wiki-api.hoyolab.com/hoyowiki/genshin/wapi/get_entry_page_list'
    total = 30
    chunk = 50
    headers = {
        'authority': 'sg-wiki-api.hoyolab.com',
        'method': 'POST',
        'path': '/hoyowiki/genshin/wapi/get_entry_page_list',
        'scheme': 'https',
        'accept': 'application/json, text/plain, */*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7',
        'origin': 'https://wiki.hoyolab.com',
        'referer': 'https://wiki.hoyolab.com',
        # 'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Google Chrome";v="110"',
        # 'sec-ch-ua-mobile': '?0',
        # 'sec-ch-ua-platform': '"Windows"',
        # 'sec-fetch-dest': 'empty',
        # 'sec-fetch-mode': 'cors',
        # 'sec-fetch-site': 'same-site',
        'x-rpc-language': 'ja-jp',
        'x-rpc-wiki_app': 'genshin',
        'Content-Type': 'application/json;charset=UTF-8',
        # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
    }
    result = []
    page_num = 1
    while page_num <= math.ceil(total / chunk):
        body = {
            'filters': [],
            'menu_id': str(menu_id),
            'page_num': page_num,
            'page_size': chunk,
            'use_es': True
        }
        response = requests.post(url, headers=headers, data=dumps(body))
        res_data = loads(response.text)
        c_list = res_data['data']['list']
        result.extend(c_list)
        if page_num == 1:
            total = int(res_data['data']['total'])
        page_num += 1
    return result


#################################
#
# キャラクター情報更新用処理
#
#################################


# HoYoWikiのキャラ一覧取得APIを叩いて
# 全キャラ一覧を取得する
def request_chara_list():
    return __request_page_list('2')


# HoYoWikiのキャラ情報取得APIを叩いて
# キャラ1人の詳細情報を取得する
def request_chara_data(chara_id):
    url = f'https://sg-wiki-api-static.hoyolab.com/hoyowiki/genshin/wapi/entry_page?entry_page_id={chara_id}'
    headers = {
        'authority': 'sg-wiki-api.hoyolab.com',
        'method': 'GET',
        'path': f'/hoyowiki/genshin/wapi/entry_page?entry_page_id={chara_id}',
        'scheme': 'https',
        'accept': 'application/json, text/plain, */*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7',
        'origin': 'https://wiki.hoyolab.com',
        'referer': 'https://wiki.hoyolab.com',
        'x-rpc-language': 'ja-jp',
        'x-rpc-wiki_app': 'genshin',
        'Content-Type': 'application/json;charset=UTF-8',
    }
    response = requests.get(url, headers=headers)
    # with open(f'response_chara_{chara_id}.json', 'w', encoding='utf-8', newline='\n') as f:
    #     f.write(response.text)
    result = loads(response.text)
    return result


# キャラ情報から立ち絵・アイコンの画像URLを抜き出す
def get_chara_images(chara_data):
    result = dict()
    datas = chara_data['data']['page']['modules']
    # キャラクターイラスト
    gallery = [
        loads(data['components'][0]['data'])
        for data in datas
        if data['name'] == 'ギャラリー'
    ][0]
    result['avatar'] = [
        data['img']
        for data in gallery['list']
        if data['key'] == '原画'
    ][0]
    # 準備中のキャラは立ち絵がないのでNoneを返す
    if not result['avatar']:
        print('準備中のキャラクターのため、立ち絵が存在しません。')
        return None
    # 天賦アイコン
    # 通常は名前に「通常攻撃」が入ってる
    # スキル・爆発は天賦レベルがLv15まである
    # スキルと爆発は「元素エネルギー」項目の有無で識別可能
    talent = [
        loads(data['components'][0]['data'])
        for data in datas
        if data['name'] == '天賦'
    ][0]
    # talent_a = [
    #     t_data['icon_url']
    #     for t_data in talent['list']
    #     if '通常攻撃' in t_data['key']
    # ][0]
    # talent_s = [
    #     t_data['icon_url']
    #     for t_data in talent['list']
    #     if t_data['attributes'] is not None and
    #         len(t_data['attributes']) > 0 and
    #         len(t_data['attributes'][0]['values']) >= 13 and
    #         not any([
    #             attr['key'] == '元素エネルギー'
    #             for attr in t_data['attributes']
    #         ])
    # ][0]
    # talent_e = [
    #     t_data['icon_url']
    #     for t_data in talent['list']
    #     if t_data['attributes'] is not None and
    #         len(t_data['attributes']) > 0 and
    #         len(t_data['attributes'][0]['values']) >= 13 and
    #         any([
    #             attr['key'] == '元素エネルギー'
    #             for attr in t_data['attributes']
    #         ])
    # ][0]
    attack_talents = [
        t_data['icon_url']
        for t_data in talent['list']
        if t_data['attributes'] is not None
        and len(t_data['attributes']) > 0
        and len(t_data['attributes'][0]['values']) >= 10
    ]
    result['talent'] = dict(
        a=attack_talents[0],
        s=attack_talents[1],
        e=attack_talents[2],
    )
    # 命ノ星座アイコン
    affix = [
        loads(data['components'][0]['data'])
        for data in datas
        if data['name'] == '命ノ星座'
    ][0]
    result['affix'] = [
        el['icon_url']
        for el in affix['list']
    ]
    return result


# キャラクターの立ち絵・アイコンをローカルに保存する
def save_chara_images(chara_images, out_dir):
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    # キャラクターイラスト
    # memo: 旅人のキャラクターイラストは共通のためavatarがない
    if chara_images.get('avatar'):
        save_avatar_image(chara_images['avatar'], os.path.join(out_dir, 'avatar.png'))
    # 天賦
    save_image(chara_images['talent']['a'], os.path.join(out_dir, '通常.png'))
    save_image(chara_images['talent']['s'], os.path.join(out_dir, 'スキル.png'))
    save_image(chara_images['talent']['e'], os.path.join(out_dir, '爆発.png'))
    # 命ノ星座
    for i, url in enumerate(chara_images['affix']):
        save_image(url, os.path.join(out_dir, f'{i+1}.png'))


def update_character(chara_name, chara_id):
    chara_data = request_chara_data(chara_id)
    chara_imgs = get_chara_images(chara_data)
    if chara_imgs is None:
        return False
    # 旅人のキャラクターイラストは全元素共通のためダウンロードしない
    if '旅人' in chara_name:
        chara_imgs['avatar'] = None
    save_chara_images(chara_imgs, os.path.join(
        CHARA_DIR, chara_name))
    return True


# キャラクターデータ更新処理
def update_characters(update_list):
    # HoYoWikiからキャラクターの一覧を取得して、新キャラがいるか確認する
    chara_list = request_chara_list()
    characters_data = {
        c_data['name']: c_data['entry_page_id']
        for c_data in chara_list
    }
    new_characters = dict(characters_data.items() - update_list['characters'].items())
    # 新キャラの更新
    updated_characters = dict()
    for chara_id, name in new_characters.items():
        # 正常に更新できたキャラは追加する
        if update_character(name, chara_id):
            updated_characters[chara_id] = name
    # 正常に更新できたキャラ一覧を返す
    return updated_characters


#################################
#
# コスチューム更新用処理
#
#################################


def load_document_json(file_name):
    file_path = os.path.join(
        cwd, 'docs', 'store', file_name)
    with open(file_path, 'r', encoding='utf-8') as f:
        data = f.read()
    result = loads(data)
    return result


def update_costumes(update_list):
    costumes_id_list = list(update_list['costumes'].keys())
    characters = load_document_json('characters.json')
    loc = load_document_json('loc.json')['ja']
    # 新しいコスチュームを更新する
    updated_costumes = dict()
    for chara_data in characters.values():
        # 各キャラクターのキャラ名とコスチューム一覧を取得
        chara_name_id = chara_data.get('NameTextMapHash')
        if not chara_name_id:
            continue
        chara_name = loc.get(str(chara_name_id))
        if not chara_name:
            continue
        chara_costumes = chara_data.get('Costumes')
        if not chara_costumes:
            continue
        # 1キャラに複数のコスチュームがある場合も、全て取得する
        # 新しいコスチュームがあれば更新する
        for k, v in chara_costumes.items():
            print(k)
            if k in costumes_id_list:
                continue
            image_name = v['art']
            print(f'名前: {chara_name}, 画像: {image_name}')
            is_save = save_avatar_image(
                f'https://enka.network/ui/{image_name}.png',
                os.path.join(CHARA_DIR, chara_name, f'{k}.png')
            )
            if not is_save:
                print('更新失敗')
                continue
            print('更新！')
            updated_costumes[k] = image_name
    # 更新できたコスチュームの一覧を返す
    return updated_costumes



#################################
#
# 武器情報更新用処理
#
#################################


# HoYoWikiの武器一覧取得APIを叩いて
# 全武器一覧を取得する
def request_weapon_list():
    return __request_page_list('4')


# 全武器一覧から必要なデータのみ抽出する
# （「武器名称: 画像URL」の辞書を返す）
def get_weapons_data(weapon_list):
    result = dict()
    for w_data in weapon_list:
        w_name = w_data['name']
        w_icon_url = w_data['icon_url']
        result[w_name] = w_icon_url
    return result


# 武器データ更新処理
def update_weapons(update_list):
    # HoYoWikiから武器の一覧を取得して、新武器があるか確認する
    weapon_list = request_weapon_list()
    weapons_data = get_weapons_data(weapon_list)
    new_weapons = dict(weapons_data.items() - update_list['weapons'].items())
    # 新武器の更新
    updated_weapons = dict()
    for name, url in new_weapons.items():
        save_image(url, os.path.join(
            WEAPON_DIR, f'{name}.png'))
        # 正常に更新できた武器は追加する
        updated_weapons[name] = url
    # 正常に更新できた武器一覧を返す
    return updated_weapons


#################################
#
# 聖遺物情報更新用処理
#
#################################


# HoYoWikiの聖遺物一覧取得APIを叩いて
# 全聖遺物一覧を取得する
def request_artifact_list():
    return __request_page_list('5')


# 全聖遺物一覧から必要なデータのみ抽出する
def get_artifacts_data(artifact_list):
    result = dict()
    for a_data in artifact_list:
        a_name = a_data['name']
        a_icon_urls = dict(
            flower=a_data['display_field'].get('flower_of_life_icon_url'),
            wing=a_data['display_field'].get('plume_of_death_icon_url'),
            clock=a_data['display_field'].get('sands_of_eon_icon_url'),
            cup=a_data['display_field'].get('goblet_of_eonothem_icon_url'),
            crown=a_data['display_field'].get('circlet_of_logos_icon_url'),
        )
        result[a_name] = dumps(a_icon_urls, ensure_ascii=False)
    return result


# 聖遺物のアイコンをローカルに保存する
def save_artifact_icons(icon_urls, out_dir):
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    for name, url in icon_urls.items():
        if not url:
            continue
        save_image(url, os.path.join(out_dir, f'{name}.png'))


# 聖遺物データ更新処理
def update_artifacts(update_list):
    # HoYoWikiから聖遺物の一覧を取得して、新聖遺物があるか確認する
    artifact_list = request_artifact_list()
    artifacts_data = get_artifacts_data(artifact_list)
    new_artifacts = dict(artifacts_data.items() - update_list['artifacts'].items())
    # 新聖遺物の更新
    updated_artifacts = dict()
    for name, data in new_artifacts.items():
        icon_urls = loads(data)
        save_artifact_icons(icon_urls, os.path.join(
            ARTIFACT_DIR, name))
        # 正常に更新できた聖遺物は追加する
        updated_artifacts[name] = data
    # 正常に更新できた聖遺物一覧を返す
    return updated_artifacts


def update_images(
        chara_name, costume_id, costume_name, weapon_name, artifact_names):
    print(
        '画像更新します。'
        f' {chara_name=} {costume_id=} {costume_name=}'
        f' {weapon_name=} {artifact_names=}'
    )
    is_change = False
    update_list = load_update_list()
    # キャラクターの画像がなければダウンロードする
    if not os.path.exists(os.path.join(CHARA_DIR, chara_name)):
        # update_listに情報がなければHoYoWikiからキャラ一覧を取得して更新する
        if chara_name not in update_list['characters']:
            chara_list = request_chara_list()
            update_list['characters'] = {
                c_data['name']: c_data['entry_page_id']
                for c_data in chara_list
            }
            is_change = True
        chara_id = update_list['characters'][chara_name]
        # HoYoWikiのキャラ情報を取得し、画像更新する
        update_character(chara_name, chara_id)
    # コスチューム更新
    costume_path = os.path.join(
        CHARA_DIR, chara_name, f'{costume_id}.png')
    if costume_id is not None and \
            not os.path.exists(costume_path):
        save_avatar_image(
            f'https://enka.network/ui/{costume_name}.png',
            costume_path
        )
    # 武器更新
    weapon_path = os.path.join(
        WEAPON_DIR, f'{weapon_name}.png')
    if not os.path.exists(weapon_path):
        if weapon_name not in update_list['weapons']:
            weapon_list = request_weapon_list()
            update_list['weapons'] = get_weapons_data(weapon_list)
            is_change = True
        save_image(
            update_list['weapons'][weapon_name], weapon_path)
    # 聖遺物更新
    for a_name in artifact_names:
        artifact_path = os.path.join(ARTIFACT_DIR, a_name)
        if not os.path.exists(artifact_path):
            if a_name not in update_list['artifacts']:
                artifact_list = request_artifact_list()
                update_list['artifacts'] = get_artifacts_data(artifact_list)
                is_change = True
            icon_urls = loads(update_list['artifacts'][a_name])
            save_artifact_icons(icon_urls, artifact_path)
    print(
        '画像更新しました。'
        f' {chara_name=} {costume_id=} {costume_name=}'
        f' {weapon_name=} {artifact_names=}'
    )
    # update_listを更新する
    if is_change:
        print('update_listを更新します。')
        save_update_list(update_list)
        print('update_listを更新しました。')
    return True


def main(version):
    update_list = load_update_list()
    # キャラ更新
    try:
        updated_chara = update_characters(update_list)
        update_list['characters'].update(updated_chara)
        print('キャラクター更新')
    except Exception as e:
        print('キャラクター更新でエラーが発生しました。')
        print(e)
        raise e
    # コスチューム更新
    try:
        updated_costumes = update_costumes(update_list)
        update_list['costumes'].update(updated_costumes)
        print('コスチューム更新')
    except Exception as e:
        print('コスチューム更新でエラーが発生しました。')
        print(e)
        raise e
    # 武器更新
    try:
        updated_weapon = update_weapons(update_list)
        update_list['weapons'].update(updated_weapon)
        print('武器更新')
    except Exception as e:
        print('武器更新でエラーが発生しました。')
        print(e)
        raise e
    # 聖遺物更新
    try:
        updated_artifacts = update_artifacts(update_list)
        update_list['artifacts'].update(updated_artifacts)
        print('聖遺物更新')
    except Exception as e:
        print('聖遺物更新でエラーが発生しました。')
        print(e)
        raise e
    save_update_list(update_list)


if __name__ == '__main__':
    main()
