from copy import deepcopy
from unittest import TestCase

from unittest.mock import patch, Mock

from pony.orm import db_session, rollback
from vk_api.bot_longpoll import VkBotMessageEvent

from bot import Bot
import settings
from generate_ticket import generate_invitation


def isolate_db(test_func):
    def wrapper(*args, **kwargs):
        with db_session:
            test_func(*args, **kwargs)
            rollback()
    return wrapper


class Test1(TestCase):

    RAW_EVENT = {'type': 'message_new',
                 'object': {'date': 1642292669, 'from_id': 557031913, 'id': 88, 'out': 0, 'peer_id': 557031913,
                            'text': 'hello', 'conversation_message_id': 84, 'fwd_messages': [], 'important': False,
                            'random_id': 0, 'attachments': [], 'is_hidden': False},
                 'group_id': 209969541,
                 'event_id': '55dd61a195f026b8c5da9cf870c8b78d025151f1'}

    def test_run(self):
        count = 5
        events = [{}] * count
        long_poller_mock = Mock(return_value=events)
        long_poller_listen_mock = Mock()
        long_poller_listen_mock.listen = long_poller_mock

        with patch('bot.vk_api.VkApi'):
            with patch('bot.VkBotLongPoll', return_value=long_poller_listen_mock):
                bot = Bot('', '')
                bot.on_event = Mock()
                bot.send_image = Mock()
                bot.run()

                bot.on_event.assert_called()
                bot.on_event.assert_any_call({})
                assert bot.on_event.call_count == count

    INPUTS = [
        'Привет',
        'А когда будет конференция?',
        'Где будет конференция?',
        'до какого числа можно подать заявку на конференцию?',
        'какие направления будут на конференции?',
        'могу ли я изменить ранее поданную заявку?',
        'хочу удалить заявку. Как мне это сделать?',
        'могу ли я подать заявку без указания научного руководителя?',
        'если я не являюсь студентом, можно ли мне участвовать в конференции?',
        'кто может участвовать в конференции?',
        'аспиранты могут участвовать в конференции?',
        'сертификаты будут выдавать?',
        'спасибо за ответ',
        'Зарегистрируй меня',
        'Сомов Алексей',
        'Сомов Алексей Михайлович',
        'мой адрес alex@email',
        'alex@email.ru',
        'СПбГУ',
        'компьютерная и прикладная лингвистика',
        'магистратура',
        '2',
        'Анализ тональности новостных текстов',
        'дискурс анализ',
        'компьютерная и прикладная лингвистика',
        'Николай Петрович',
        'Иванов Николай Петрович',
        'да'
    ]
    EXPECTED_OUTPUTS = [
        settings.INTENTS[10]['answer'],
        settings.INTENTS[0]['answer'],
        settings.INTENTS[1]['answer'],
        settings.INTENTS[2]['answer'],
        settings.INTENTS[3]['answer'],
        settings.INTENTS[4]['answer'],
        settings.INTENTS[5]['answer'],
        settings.INTENTS[6]['answer'],
        settings.INTENTS[7]['answer'],
        settings.INTENTS[7]['answer'],
        settings.INTENTS[7]['answer'],
        settings.INTENTS[8]['answer'],
        settings.INTENTS[9]['answer'],
        settings.SCENARIOS['registration']['steps']['step1']['text'],
        settings.SCENARIOS['registration']['steps']['step1']['failure_text'],
        settings.SCENARIOS['registration']['steps']['step2']['text'],
        settings.SCENARIOS['registration']['steps']['step2']['failure_text'],
        settings.SCENARIOS['registration']['steps']['step3']['text'],
        settings.SCENARIOS['registration']['steps']['step4']['text'],
        settings.SCENARIOS['registration']['steps']['step5']['text'],
        settings.SCENARIOS['registration']['steps']['step6']['text'],
        settings.SCENARIOS['registration']['steps']['step7']['text'],
        settings.SCENARIOS['registration']['steps']['step8']['text'],
        settings.SCENARIOS['registration']['steps']['step8']['failure_text'],
        settings.SCENARIOS['registration']['steps']['step9']['text'],
        settings.SCENARIOS['registration']['steps']['step9']['failure_text'],
        settings.SCENARIOS['registration']['steps']['step10']['text'].format(name='Сомов Алексей Михайлович',
                                                                             email='alex@email.ru',
                                                                             university='СПбГУ',
                                                                             faculty='компьютерная и прикладная '
                                                                                     'лингвистика',
                                                                             program='магистратура',
                                                                             year_of_study='2',
                                                                             report='Анализ тональности новостных '
                                                                                    'текстов',
                                                                             section='компьютерная и прикладная '
                                                                                     'лингвистика',
                                                                             scientific_supervisor='Иванов Николай '
                                                                                                   'Петрович',
                                                                             ),
        settings.SCENARIOS['registration']['steps']['step11']['text'].format(name='Сомов Алексей Михайлович',
                                                                             email='alex@email.ru')
    ]

    @isolate_db
    def test_run_ok(self):
        send_mock = Mock()
        api_mock = Mock()
        api_mock.messages.send = send_mock

        events = []
        for input_text in self.INPUTS:
            event = deepcopy(self.RAW_EVENT)
            event['object']['text'] = input_text
            events.append(VkBotMessageEvent(event))

        long_poller_mock = Mock()
        long_poller_mock.listen = Mock(return_value=events)

        with patch('bot.VkBotLongPoll', return_value=long_poller_mock):
            bot = Bot('', '')
            bot.api = api_mock
            bot.send_image = Mock()
            bot.run()

        assert send_mock.call_count == len(self.INPUTS)

        real_outputs = []
        for call in send_mock.call_args_list:
            args, kwargs = call
            real_outputs.append(kwargs['message'])
        assert real_outputs == self.EXPECTED_OUTPUTS

    def test_generate_invitation(self):

        ticket_file = generate_invitation('Сомова Анна Алексеевна', 'Анализ тональности новостных текстов')

        with open('files/invitation_example.png', 'rb') as expected_file:
            expected_bytes = expected_file.read()

        assert ticket_file.read() == expected_bytes
