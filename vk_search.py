import vk_api
from vk_api.exceptions import ApiError
import requests
import traceback


class Vk_search:

    AGES_LIST = ['18-25', '25-35', '35-40', '40-50']

    fields = 'bdate,activities,about,blacklisted,blacklisted_by_me,books,can_be_invited_group,can_post,' \
        'can_see_all_posts,can_see_audio,can_send_friend_request,can_write_private_message,career,connections,' \
        'contacts,city,country,crop_photo,domain,education,exports,followers_count,friend_status,has_photo,' \
        'has_mobile,home_town,photo_100,photo_200,photo_200_orig,photo_400_orig,photo_50,sex,site,schools,' \
        'screen_name,status,verified,games,interests,is_favorite,is_friend,is_hidden_from_feed,last_seen,' \
        'maiden_name,military,movies,music,nickname,occupation,online,personal,photo_id,photo_max,' \
        'photo_max_orig,quotes,relation,relatives,timezone,tv,universities'

    def __init__(self, api, app_token):
        self.api = api
        self.app_token = app_token
        self.app_api = vk_api.VkApi(token=app_token).get_api()
        self._search_params = {
            'photo': 1,
            'domain': 1,
            'site': 1,
            'count': 3,
            'offset': 0,
            'has_photo': 1
        }
        self.users = None

    @property
    def sex(self):
        return self._search_params.get('sex')

    @sex.setter
    def sex(self, request):
        self._search_params['sex'] = 2 if request == 'М' else 1

    @property
    def age(self):
        return f"{self._search_params.get('age_from')}-{self._search_params.get('age_to')}"

    @age.setter
    def age(self, request):
        self._search_params['age_from'] = request.split('-')[0]
        self._search_params['age_to'] = request.split('-')[1]

    @property
    def city(self):
        return self._search_params.get('city')

    @city.setter
    def city(self, request):
        city = self._get_city(request).get('items')
        if city:
            city_id = city[0].get('id')
            self._search_params['city'] = city_id

    def get_client(self, user_id):
        user = self.api.users.get(user_ids=str(user_id), fields=self.fields)[0]
        self.client_city = user.get('city').get('title')
        return user

    def _get_search_fields(self, params):
        fields_list = [f'{k}={v}' for k, v in params.items()]
        return ','.join(fields_list)

    def search_by_params(self):
        return self.app_api.users.search(
            **self._search_params,
            fields='domain'
            )

    def _get_city(self, request):
        return self.app_api.database.getCities(q=request)

    def get_user(self):
        if not self.users:
            self.users = iter(self.search_by_params()['items'])
        try:
            self.user = next(self.users)
            if self.user['is_closed']:
                return self.get_user()
            else:
                return self.user 
        except StopIteration:
            self._search_params['offset'] += 100
            self.users = self.search_by_params()['items']
            if not self.users:
                return
            else:
                self.users = iter(self.users)
                return self.get_user() 

    def get_photos(
        self,
        user_id,
        album_id: str = 'profile',
        extended: int = 1,
        photo_sizes: int = 1,
        count: int = 100
    ) -> dict:
        params = {
            'owner_id': user_id,
            'album_id': album_id,
            'extended': extended,
            'photo_sizes': photo_sizes,
            'count': 100,
            'offset': 0
        }
        try:
            photos = self.app_api.photos.get(**params).get('items')
            photos.sort(key=lambda photo: photo.get('likes').get('count'), reverse=True)
            self.photos = photos[:3]
            return self.photos
        except ApiError:
            print('Ошибка:\n', traceback.format_exc())


        

