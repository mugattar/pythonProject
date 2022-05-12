#!/usr/bin/env python3

import logging.config

from pony.orm import db_session
import requests

from log_settings import log_config
import handlers
import random
from models import UserState, Registration
import settings

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

logging.config.dictConfig(log_config)
log = logging.getLogger('bot')


class Bot:
    """
    Chatbot for the community on vk.com

    Use python 3.10
    """

    def __init__(self, group_id, token):
        """
        :param group_id: group id from the community on vk.com
        :param token: secret token from the community on vk.com
        """
        self.group_id = group_id
        self.token = token
        self.vk = vk_api.VkApi(token=token)
        self.long_poller = VkBotLongPoll(self.vk, self.group_id)
        self.api = self.vk.get_api()

    def run(self):
        """
        Launches the chatbot
        :return: None
        """
        for event in self.long_poller.listen():
            try:
                self.on_event(event)
            except Exception as exc:
                log.exception(f'ошибка в обработке события', {exc})

    @db_session
    def on_event(self, event):
        """
        Handles the event
        :param event: VkBotMessageEvent object
        :return: None
        """
        if event.type != VkBotEventType.MESSAGE_NEW:
            log.info('события такого типа не обрабатываются %s', event.type)
            return
        user_id = event.object.peer_id
        text = event.object.text
        state = UserState.get(user_id=str(user_id))
        for intent in settings.INTENTS:
            log.debug(f'Интент, полученный от пользователя {intent}')
            if any(token in text.lower() for token in intent['tokens']):
                if intent['answer']:
                    self.send_text(intent['answer'], user_id)
                else:
                    if state:
                        state.delete()
                    self.start_scenario(user_id, intent['scenario'], text)
                break
        else:
            if state is not None:
                self.continue_scenario(text, state, user_id)
            else:
                self.send_text(settings.DEFAULT_ANSWER, user_id)

    def send_text(self, text_to_send, user_id):
        self.api.messages.send(message=text_to_send,
                               random_id=random.randint(0, 2 ** 20),
                               peer_id=user_id)

    def send_image(self, image, user_id):
        upload_url = self.api.photos.getMessagesUploadServer()['upload_url']
        upload_data = requests.post(url=upload_url, files={'photo': ('image.png', image, 'image/png')}).json()
        image_data = self.api.photos.saveMessagesPhoto(**upload_data)
        owner_id = image_data[0]['owner_id']
        media_id = image_data[0]['id']
        attachment = f'photo{owner_id}_{media_id}'
        self.api.messages.send(
            attachment=attachment,
            random_id=random.randint(0, 2 ** 20),
            peer_id=user_id)

    def send_step(self, step, user_id, text, context):
        if 'text' in step:
            self.send_text(step['text'].format(**context), user_id)
        if 'image' in step:
            handler = getattr(handlers, step['image'])
            image = handler(text, context)
            self.send_image(image, user_id)

    def start_scenario(self, user_id, scenario_name, text):
        scenario = settings.SCENARIOS[scenario_name]
        first_step = scenario['first_step']
        step = scenario['steps'][first_step]
        self.send_step(step, user_id, text, context={})
        UserState(user_id=str(user_id), scenario_name=scenario_name, step_name=first_step, context={})

    def continue_scenario(self, text, state, user_id):
        steps = settings.SCENARIOS[state.scenario_name]['steps']
        step = steps[state.step_name]
        handler = getattr(handlers, step['handler'])
        if handler(text=text, context=state.context):
            next_step = steps[step['next_step']]
            self.send_step(next_step, user_id, text, state.context)
            if next_step['next_step']:
                state.step_name = step['next_step']
            else:
                Registration(name=state.context['name'],
                             email=state.context['email'],
                             university=state.context['university'],
                             report=state.context['report'],
                             section=state.context['section'],
                             scientific_supervisor=state.context['scientific_supervisor'])
                state.delete()
        else:
            text_to_send = step['failure_text'].format(**state.context)
            self.send_text(text_to_send, user_id)


if __name__ == '__main__':
    bot = Bot(settings.GROUP_ID, settings.TOKEN)
    bot.run()



