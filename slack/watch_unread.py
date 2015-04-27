#!/usr/bin/env python3

import sys
import os
import time
import datetime
import requests

show_msg_length = int(os.environ.get('SLACK_SHOW_MSG_LENGTH', 15))
watch_interval = int(os.environ.get('SLACK_WATCH_INTERVAL', 10))
token = os.environ['SLACK_API_TOKEN']
api_urls = dict(
    channel_list='https://slack.com/api/channels.list',
    channel_info='https://slack.com/api/channels.info',
    group_list='https://slack.com/api/groups.list',
    group_info='https://slack.com/api/groups.info'
)


def watching_channels():
    chs = os.environ.get('SLACK_WATCH_CHANNELS')
    if chs is not None:
        return chs.split(',')
    else:
        return list()


def watching_groups():
    grs = os.environ.get('SLACK_WATCH_GROUPS')
    if grs is not None:
        return grs.split(',')
    else:
        return list()


def channel_list():
    params = {'token': token}
    r = requests.get(api_urls['channel_list'], params=params)
    return r.json()['channels']


def channel_info(ch_id):
    params = {'token': token, 'channel': ch_id}
    r = requests.get(api_urls['channel_info'], params=params)
    return r.json()['channel']


def group_info(gr_id):
    params = {'token': token, 'channel': gr_id}
    r = requests.get(api_urls['group_info'], params=params)
    return r.json()['group']


def group_list():
    params = {'token': token}
    r = requests.get(api_urls['group_list'], params=params)
    return r.json()['groups']


targets = list()

for channel in channel_list():
    if channel['name'] in watching_channels():
        targets.append(
            {'type': 'channel', 'id': channel['id'], 'name': channel['name']}
        )

for group in group_list():
    if group['name'] in watching_groups():
        targets.append(
            {'type': 'group', 'id': group['id'], 'name': group['name']}
        )

while True:
    msg = ''

    for target in targets:
        if target['type'] == 'channel':
            info = channel_info(target['id'])
        else:
            info = group_info(target['id'])

        unread = info['unread_count_display']

        if unread is not 0:
            msg += "[%s(%s): %s] " % (
                target['name'],
                info['unread_count_display'],
                info['latest']['text'][0:show_msg_length]
            )

    if msg == '':
        msg = 'unread message not found in Slack'

    t = datetime.datetime.today().strftime('%H:%M:%S')
    msg = '%s ' % t + msg

    print(msg)
    sys.stdout.flush()
    time.sleep(watch_interval)
