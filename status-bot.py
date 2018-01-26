# coding:utf-8
import os
import sys
import time
import json
from ConfigParser import SafeConfigParser, MissingSectionHeaderError

from slackclient import SlackClient
from logbook import Logger
from logbook import RotatingFileHandler
from logbook import StreamHandler

SLACK_SECTION_NAME = "slack"
logger = Logger("status-bot")


def is_status_changed_event(res):
    return res["type"] == "user_change"

def is_target_status_emoji(profile):
    return profile["status_emoji"] == target_status

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
token = parse_required_option(config, "token")
room = parse_required_option(config, "room")
target_status = parse_required_option(config, "status")
message_format_on = parse_required_option(config, "message_format_on")
setup_logger(config)
sc = SlackClient(token)

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
                    name = "@" + user["name"]
                    if is_target_status_emoji(profile):
                        text = message_format_on.format(name)
                        sc.api_call("chat.postMessage", channel=room, text=text, as_user="1")

else:
    logger.critical("Connection Failed, invalid token?")