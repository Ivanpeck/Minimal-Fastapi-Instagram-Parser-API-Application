import requests

class UserNotFound(Exception):
    pass

class UserPrivate(Exception):
    pass

class ResourceBlocked(Exception):
    pass

def username_data(username: str):
    try:
        resp = requests.get(f'https://www.instagram.com/api/v1/users/web_profile_info/?username={username}', headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36",
            "X-IG-App-ID": "936619743392459"  # стандартный App ID Instagram Web
        }, timeout=10)

    except Exception as e:
        raise ResourceBlocked('Ресурс заблокирован! Попробуйте включить VPN')

    if resp.status_code == 404:
        raise UserNotFound('User not found')

    data = resp.json()["data"]["user"]

    if data['is_private']:
        raise UserPrivate('Profile is private')

    edges = data['edge_owner_to_timeline_media']["edges"]
    need_data = {
        "username": username,
        "full_name": data['full_name'],
        "bio": data['biography'],
        "profile_pic_url": data['profile_pic_url'],
        "followers": data['edge_followed_by']["count"],
        "following": data['edge_follow']["count"],
        "posts": data['edge_owner_to_timeline_media']["count"],
        "latest_photos": [edges[i]['node']['display_url'] for i in range(min(len(edges), 4))]

    }

    return need_data

