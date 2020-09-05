import datetime
from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db.models import Sum
from django.core.cache import cache
from blog.models import Blog
from read_statistics.utils import get_week_read_data, get_today_hot_data, get_yesterday_hot_data

def get_week_hot_data():
    today = timezone.now().date()
    date = today - datetime.timedelta(days=7)
    blogs = Blog.objects\
        .filter(read_details__date__gte=date, read_details__date__lt=today)\
        .values("id", "title")\
        .annotate(read_num_sum=Sum('read_details__read_num'))\
        .order_by('-read_num_sum')
    return blogs[:7]

def home(request):
    blog_content_type = ContentType.objects.get_for_model(Blog)
    dates, read_nums = get_week_read_data(blog_content_type)

    # 设置缓存
    week_hot_data = get_week_hot_data()
    hot_blogs_for_week = cache.get('hot_blogs_for_week')
    if hot_blogs_for_week is None:
        hot_blogs_for_week = week_hot_data
        cache.set('hot_blogs_for_week', hot_blogs_for_week, 3600)

    context = {}
    context['dates'] = dates
    context['read_nums'] = read_nums
    context['today_hot_data'] = get_today_hot_data(blog_content_type)
    context['yesterday_hot_data'] = get_yesterday_hot_data(blog_content_type)
    context['week_hot_data'] = week_hot_data
    return render(request, 'home.html', context)

