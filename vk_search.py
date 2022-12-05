import vk_api
import traceback
from vk_api.exceptions import ApiError


class Vk_search:

    fields = 'bdate,activities,about,blacklisted,blacklisted_by_me,books,'\
        'can_be_invited_group,can_post,' \
        'can_see_all_posts,can_see_audio,can_send_friend_request,' \
        'can_write_private_message,career,connections,' \
        'contacts,city,country,crop_photo,domain,education,exports,' \
        'followers_count,friend_status,has_photo,' \
        'has_mobile,home_town,photo_100,photo_200,photo_200_orig,' \
        'photo_400_orig,photo_50,sex,site,schools,' \
        'screen_name,status,verified,games,interests,' \
        'is_favorite,is_friend,is_hidden_from_feed,last_seen,' \
        'maiden_name,military,movies,music,nickname,occupation,' \
        'online,personal,photo_id,photo_max,' \
        'photo_max_orig,quotes,relation,relatives,timezone,tv,universities'

    def __init__(self, api, app_token):
        self.api = api
        self.app_token = app_token
        self.app_api = vk_api.VkApi(token=app_token).get_api()
        self._search_params = {
            'photo': 1,
            'domain': 1,
            'site': 1,
            'count': 10,
            'offset': 0,
            'has_photo': 1,
            'is_closed': 0,
        }

    def get_sex(self, request):
        return 2 if request == 'М' else 1

    def get_city(self, request):
        city = self._get_city(request).get('items')
        if city:
            return city[0].get('id')

    def check_token(self):
        try:
            return self.app_api.apps.get()
        except ApiError:
            print('Ошибка:\n', traceback.format_exc())

    def get_client(self, user_id):
        user = self.api.users.get(user_ids=str(user_id), fields=self.fields)[0]
        self.client_city = user.get('city').get('title')
        return user

    def search_by_params(self):
        return self.app_api.users.search(
            **self._search_params,
            fields='domain'
        )

    def _get_city(self, request):
        return self.app_api.database.getCities(q=request)

    def get_photos(
        self,
        user_id,
        album_id: str = 'profile',
        extended: int = 1,
        photo_sizes: int = 1,
        count: int = 100
    ):
        params = {
            'owner_id': user_id,
            'album_id': album_id,
            'extended': extended,
            'photo_sizes': photo_sizes,
            'count': count,
            'offset': 0
        }
        try:
            photos = self.app_api.photos.get(**params).get('items')
            photos.sort(
                key=lambda photo: photo.get('likes').get('count'), reverse=True
            )
            self.photos = photos[:3]
            return self.photos
        except ApiError:
            print('Ошибка:\n', traceback.format_exc())

    def convert_param(self, key, value=None):
        return {
            'Пол': ('sex', self.get_sex(value)),
            'Город': ('city_id', self.get_city(value)),
            'Возраст от': ('age_from', value),
            'Возраст до': ('age_to', value),
        }[key]

    def _set_search_params(self, params):
        for k, v in params.items():
            new_key, new_val = self.convert_param(k, v[0])
            self._search_params[new_key] = new_val

    def get_users(self, params, offset):
        self._set_search_params(params)
        self._search_params['offset'] = offset
        print(self._search_params)
        users = self.search_by_params()['items']
        users = list(filter(lambda user: not user['is_closed'], users))
        return users
