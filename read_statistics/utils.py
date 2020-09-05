import datetime
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db.models import Sum
from .models import ReadNum, ReadDetail

def read_statistics_once_read(request, obj):
    ct = ContentType.objects.get_for_model(obj)
    key = "%s_%s_read" % (ct.model, obj.pk)
    if not request.COOKIES.get(key):
        '''
        if ReadNum.objects.filter(content_type=ct, object_id=obj.pk).count():
            readnum = ReadNum.objects.get(content_type=ct, object_id=obj.pk)
        else:
            readnum = ReadNum(content_type=ct, object_id=obj.pk)
        '''
        # get_or_create表示有数据就取出来，没有就创建
        # 此处是对当前文章的阅读增加次数
        readnum, created = ReadNum.objects.get_or_create(content_type=ct, object_id=obj.pk)
        readnum.read_num += 1
        readnum.save()

        # 统计每一天各文章的阅读数
        date = timezone.now().date()
        per_day_readnum, created = ReadDetail.objects.get_or_create(date=date, content_type=ct, object_id=obj.pk)
        per_day_readnum.read_num += 1
        per_day_readnum.save()
    return key

def get_week_read_data(content_type):
    today = timezone.now().date()
    dates = []
    read_nums = []
    for i in range(7, 0, -1):
        date = today - datetime.timedelta(days=i)
        read_details = ReadDetail.objects.filter(content_type=content_type, date=date)
        result = read_details.aggregate(read_num_sum=Sum('read_num'))
        read_nums.append(result['read_num_sum'] or 0)
        dates.append(date.strftime('%m/%d'))
    return  dates, read_nums

def get_hot_data(content_type, date):
    read_details = ReadDetail.objects.filter(content_type=content_type, date=date).order_by('-read_num')
    return read_details

def get_today_hot_data(content_type):
    today = timezone.now().date()
    read_details = get_hot_data(content_type, today)
    return read_details[:7]

def get_yesterday_hot_data(content_type):
    yesterday = timezone.now().date() - datetime.timedelta(days=1)
    read_details = get_hot_data(content_type, yesterday)
    return read_details[:7]

