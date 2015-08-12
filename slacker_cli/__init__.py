#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Send message to Slack from command line
"""

from slacker import Slacker
from slacker.utils import get_item_id_by_name
import argparse
import sys
import os
import warnings
warnings.filterwarnings('ignore', message=".*InsecurePlatformWarning.*")

def get_dict_list(dl, key, value):
    for d in dl:
        if d[key] == value:
            return d
    else:
        return None

def post_message(token, channel, message, name, icon, as_user):
    slack = Slacker(token)
    slack.chat.post_message(channel, message, username=name, icon_emoji=icon, as_user=as_user)

def get_channel_id(token, channel_name):
    slack = Slacker(token)
    channels = slack.channels.list().body['channels']
    return get_dict_list(channels, 'name', channel_name)['id']

def get_im_channel_id(token, username):
    slack = Slacker(token)
    users = slack.users.list().body['members']
    uid = get_dict_list(users, 'name', username)['id']
    ims = slack.im.list().body['ims']
    chnid = get_dict_list(ims, 'user', uid)['id']
    return chnid

def upload_file(token, channel, file_name):
    """ upload file to a channel """

    slack = Slacker(token)
    slack.files.upload(file_name, channels=channel)


def args_priority(args, environ):
    '''
        priority of token
        1) as argumment: -t
        2) as environ variable
    '''

    arg_token = args.token

    slack_token_var_name = 'SLACK_TOKEN'
    if slack_token_var_name in environ.keys():
        token = environ[slack_token_var_name]
    else:
        token = None

    if arg_token:
        token = arg_token

    return token, args.channel


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--channel", help="Slack channel")
    parser.add_argument("-u", "--user", help="Slack user")
    parser.add_argument("-t", "--token", help="Slack token")
    parser.add_argument("-f", "--file", help="File to upload")
    parser.add_argument("-n", "--name", help="Sender name")
    parser.add_argument("-s", "--asuser", help="Send as user (not as bot)", dest='as_user', action='store_true')
    parser.add_argument("-d", "--direct", help="Direct message", dest='direct', action='store_true')
    parser.add_argument("-i", "--icon-emoji", help="Sender emoji icon")

    args = parser.parse_args()

    token, channel = args_priority(args, os.environ)
    user = args.user
    name = args.name
    icon = args.icon_emoji
    file_name = args.file
    as_user = args.as_user
    direct = args.direct

    assert token

    if file_name:
        message = None
    else:
        message = sys.stdin.read()

    if direct:
        chnid = get_im_channel_id(token, user)
    else:
        if channel:
            chn = '#' + channel
        elif user:
            chn = '@' + user
        else:
            assert False
        #chnid = get_channel_id(token, chn)
        chnid = chn

    if message:
        post_message(token, chnid, message, name, icon, as_user)

    if file_name:
        upload_file(token, chnid, file_name)


if __name__ == '__main__':
    main()
