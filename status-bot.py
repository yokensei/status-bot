# coding:utf-8
import os
import sys
import time
import json
from ConfigParser import SafeConfigParser, MissingSectionHeaderError

from time import sleep
from slackclient import SlackClient
from logbook import Logger
from logbook import RotatingFileHandler
from logbook import StreamHandler

SLACK_SECTION_NAME = "slack"
logger = Logger("status-bot")


def is_status_changed_event(res):
    return res["type"] == "user_change"

def is_target_status_emoji(profile, status):
    return profile["status_emoji"] == ":" + status + ":"

def setup_logger(config):
    if config.has_option(SLACK_SECTION_NAME, "log_output"):
        output_path = config.get(SLACK_SECTION_NAME, "log_output")
        dir_path, file_name = os.path.split(output_path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        file_handler = RotatingFileHandler(output_path, backup_count=5)
        file_handler.push_application()
    else:
        stream_handler = StreamHandler(sys.stdout)
        stream_handler.push_application()


def read_config(config):
    error_message = "Please create '{}' section and contain options.".format(SLACK_SECTION_NAME)
    try:
        config.read("config.ini")
    except MissingSectionHeaderError:
        print error_message
        sys.exit()

    if not config.has_section(SLACK_SECTION_NAME):
        print error_message
        sys.exit()


def parse_required_option(config, option):
    if not config.has_option(SLACK_SECTION_NAME, option):
        print "Please setting '{}' option in '{}' section.".format(option, SLACK_SECTION_NAME)
        sys.exit()

    return config.get(SLACK_SECTION_NAME, option)


config = SafeConfigParser()
read_config(config)
slack_token = parse_required_option(config, "slack_token")
bot_token = parse_required_option(config, "bot_token")
room = parse_required_option(config, "room")
status_start = parse_required_option(config, "status_start")
status_end = parse_required_option(config, "status_end")
message_format_start = parse_required_option(config, "message_format_start")
message_format_end = parse_required_option(config, "message_format_end")
setup_logger(config)
sc = SlackClient(slack_token)
bot_sc = SlackClient(bot_token)

if sc.rtm_connect():
    logger.info("status-bot is up")

    while True:
        response = sc.rtm_read()
        for res in response:
            logger.info(res)
            if "type" in res:
                if is_status_changed_event(res):
                    user = res["user"]
                    profile = user["profile"]
                    name = user["name"]
                    if is_target_status_emoji(profile, status_start):
                        text = message_format_start.format(name)
                        bot_sc.api_call("chat.postMessage", channel=room, text=text, as_user="1")
                    if is_target_status_emoji(profile, status_end):
                        text = message_format_end.format(name)
                        bot_sc.api_call("chat.postMessage", channel=room, text=text, as_user="1")
                        new_profile = {"status_text":"","status_emoji":""}
                        sc.api_call("users.profile.set", profile=new_profile)

else:
    logger.critical("Connection Failed, invalid token?")
