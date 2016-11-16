from cookyourself.youtube import YoutubeAPI
from cookyourself.models import Dish

BASE_URL = 'https://www.youtube.com/embed/'

youtube = YoutubeAPI()
dishes = Dish.objects.all()

for dish in dishes:
    if dish.tutorial.video:
        continue

    video_id = youtube.youtube_search(dish.name)
    if not video_id:
        continue
        
    video_url = BASE_URL + video_id
    dish.tutorial.video = video_url
    print(dish.name + ": " + video_url)
    dish.tutorial.save()
