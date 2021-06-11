from mobility_5g_rest_api.models import DailyInflow


def process_daily_inflow(event, location):
    daily_inflow = DailyInflow.objects.get(date=event.timestamp.date())

    to_sum = 0
    if location == 'PT':
        to_sum = -1 if event.velocity > 0 else 1
    elif location == 'RA':
        to_sum = -1 if event.velocity < 0 else 1

    if daily_inflow:
        if daily_inflow.current <= 0 and to_sum < 0:
            to_sum = 0

        daily_inflow.current += to_sum
        daily_inflow.save()
    else:
        if to_sum < 0:
            to_sum = 0
        DailyInflow.objects.create(location='BT', date=event.timestamp.date(), current=to_sum)
