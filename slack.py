#!/usr/bin/env python

#  Copyright 2016 Mathew Odden
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import argparse
import json
import sys
import urllib2


def _get_sensu_color(event_data):
    if event_data['action'] == 'resolve':
        return 'good'

    return 'warning' if event_data['check']['status'] == 1 else 'danger'


def _parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--config')

    return p.parse_args()


def main():
    args = _parse_args()

    with open(args.config) as config_file:
        config_file_data = json.load(config_file)

    uchiwa_url = config_file_data['sensu_slack']['uchiwa_url']
    webhook_url = config_file_data['sensu_slack']['slack_webhook_url']

    event_data = json.load(sys.stdin)

    if event_data['action'] == 'create':
        # notify on the first and every 100 after
        if not (event_data.get('occurrences', 1) % 100) == 1:
            return

    fallback = ('%(client_name)s : %(check_name)s : %(check_output)s : (<%(link)s|View>)' %
                {'client_name': event_data['client']['name'],
                 'check_name': event_data['check']['name'],
                 'check_output': event_data['check']['output'],
                 'link': uchiwa_url})

    fields = [
        {'title': '',
         'value': '<%s|View in Uchiwa>' % uchiwa_url,
         'short': False}
        ]

    post = {'attachments': [
            {'fallback': fallback,
             'pretext': 'Sensu Event %sd' % event_data['action'].title(),
             'fields': fields,
             'title': '%s/%s' % (event_data['client']['name'], event_data['check']['name']),
             'text': event_data['check']['output'],
             'color': _get_sensu_color(event_data)}
           ]}

    post['username'] = 'Sensu Bot'

    payload = 'payload=%s' % json.dumps(post)
    urllib2.urlopen(webhook_url, payload)


main()
