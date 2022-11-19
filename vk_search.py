import vk_api


class Vk_search:

    fields = 'bdate,activities,about,blacklisted,blacklisted_by_me,books,can_be_invited_group,can_post,' \
        'can_see_all_posts,can_see_audio,can_send_friend_request,can_write_private_message,career,connections,' \
        'contacts,city,country,crop_photo,domain,education,exports,followers_count,friend_status,has_photo,' \
        'has_mobile,home_town,photo_100,photo_200,photo_200_orig,photo_400_orig,photo_50,sex,site,schools,' \
        'screen_name,status,verified,games,interests,is_favorite,is_friend,is_hidden_from_feed,last_seen,' \
        'maiden_name,military,movies,music,nickname,occupation,online,personal,photo_id,photo_max,' \
        'photo_max_orig,quotes,relation,relatives,timezone,tv,universities'

    def __init__(self, api, app_token):
        self.api = api
        self.app_api = vk_api.VkApi(token=app_token).get_api()

    def get_user(self, user_id):
        return self.api.users.get(user_ids=str(user_id), fields=self.fields)

    def search_by_params(self):
        return self.app_api.users.search(fields='city=Москва')
