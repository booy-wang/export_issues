# -*- coding: utf-8 -*-

import csv
import platform
import sys
import time
from datetime import datetime

import requests
from github import Github

if platform.python_version_tuple()[0] == '2':
    print('======Please use python 3.x======')
    input('Press Enter to quit...')
    sys.exit(0)


def countdown(sec):
    for i in range(sec):
        time.sleep(1)
        print('\r%d seconds left...\t\t' % (sec - i), end='')
    print('ok')


def get_current_time():
    # todo: You can change the url if you use GitHub Enterprise or other servers
    github_time = requests.get('https://api.github.com').headers['Date']  # Use https://*.github.com to get current server time.
    return time.strptime(github_time, '%a, %d %b %Y %H:%M:%S GMT')


def check_remaining():
    remain_cnt = g.get_rate_limit().core.remaining
    print('remain: %d' % remain_cnt)
    if remain_cnt < 500:  # todo: use param?
        reset_time = g.get_rate_limit().core.reset
        cur_time = get_current_time()
        print('wait until: %s' % reset_time.strftime('%Y-%m-%d %H:%M:%S UTC'))
        print('current time: %s' % time.strftime('%Y-%m-%d %H:%M:%S UTC', cur_time))
        wait_time = int(reset_time.timestamp() - time.mktime(cur_time))  # accurate to second is enough
        print('wait %d seconds until reset...' % wait_time)
        countdown(wait_time)


def get_all_issues():
    issue_list = []
    issues = repo.get_issues(state='all')
    with open('issues.csv', 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        # todo: use friendly col name?
        writer.writerow(['id', 'number', 'title', 'labels', 'milestone', 'state', 'closed_by', 'assignees', 'closed_at',
                         'created_at', 'last_modified', 'updated_at'])
        total = issues.totalCount
        cnt = 0
        print('Writing to issues.csv.....')
        check_remaining()
        for issue in issues:
            cnt += 1
            tmp_label = []
            tmp_an = []
            for l in issue.labels:
                tmp_label.append(l.name)
            for an in issue.assignees:
                if an:
                    tmp_an.append('%s<%s>' % (an.login, (an.name or an.login)))
                else:
                    tmp_an.append('')
            c_b = '' # bad var name, but I'm too lazy...
            i_m = ''
            if issue.closed_by:
                c_b = '%s<%s>' % (issue.closed_by.login, (issue.closed_by.name or issue.closed_by.login))
            if issue.milestone:
                i_m = issue.milestone.title
            if cnt % 20 == 0:  # todo: check remaining every 20 issues. need customization？
                check_remaining()
            print('getting issue %d\t %d/%d' % (issue.number, cnt, total))
            line = [issue.id,
                    issue.number,
                    issue.title,
                    ','.join(tmp_label),
                    i_m,
                    issue.state,
                    c_b,
                    ','.join(tmp_an),
                    issue.closed_at,
                    issue.created_at,
                    issue.last_modified,
                    issue.updated_at]
            writer.writerow(line)
    return issue_list


try:
    # todo: use args?
    g = Github('your access_token here')
    repos = g.get_user().get_repos()
    for repo in repos:
        if repo.full_name == 'org_name/repo_name':
            list_numbers = []
            list_select = []

            print('Retrieving issues......')
            get_all_issues()

    print('====Completed!====')
    input('Press Enter to quit...')
except Exception as e:
    print("ERROR: ", e)
    input('Press Enter to quit...')
