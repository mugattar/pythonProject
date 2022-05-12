#!/usr/bin/env python3
"""
Handler - функция, которая принимает на вход текст (текст входящего сообщения) и context (dict), а возвращает bool:
True, если шаг пройден, False, если данные введены неправильно.
"""

import re
from generate_ticket import generate_invitation
from settings import SECTIONS

re_name = re.compile(r'([А-ЯЁ][а-яё]+[\-\s]?){3,}')
re_email = re.compile(r'\b[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+\b')
re_university = re.compile(r'([А-Яa-я]+[\-\s]?){5,}')
re_report = re.compile(r'([А-Яa-я]+[\-\s]?)')


def handle_name(text, context):
    match = re.match(re_name, text)
    if match:
        context['name'] = text
        return True
    else:
        return False


def handle_email(text, context):
    matches = re.findall(re_email, text)
    if len(matches) > 0:
        context['email'] = matches[0]
        return True
    else:
        return False


def handle_university(text, context):
    match = re.match(re_university, text)
    if match:
        context['university'] = text
        return True
    else:
        return False


def handle_faculty(text, context):
    match = re.match(re_university, text)
    if match:
        context['faculty'] = text
        return True
    else:
        return False


def handle_year_of_study(text, context):
    if text.isdigit() and 0 < int(text) <= 5:
        context['year_of_study'] = text
        return True
    else:
        return False


def handle_program(text, context):
    match = re.match(re_university, text)
    if match:
        context['program'] = text
        return True
    else:
        return False


def handle_report(text, context):
    match = re.match(re_report, text)
    if match:
        context['report'] = text
        return True
    else:
        return False


def handle_section(text, context):
    for section in SECTIONS:
        if re.search(section.lower(), text.lower()):
            context['section'] = text
            return True
    return False


def handle_scientific_supervisor(text, context):
    match = re.match(re_name, text)
    if match:
        context['scientific_supervisor'] = text
        return True
    else:
        return False


def handle_confirmation(text, context):
    if text.lower() == 'да':
        context['confirmation'] = text
        return True
    else:
        return False


def generate_invitation_handler(text, context):
    return generate_invitation(name=context['name'], report=context['report'])
