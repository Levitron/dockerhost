#!/usr/bin/env python3
from dataclasses import dataclass

from lxml.etree import tostring, fromstring
from lxml.builder import E
import requests
import json
from pathlib import Path
import logging
import sys
import argparse

SCHLUND_XML_URL = 'https://gateway.schlundtech.de'
config_file_path = Path("config.json")

logging.basicConfig(filename='update-dns.log', level=logging.DEBUG, format='%(asctime)s %(name)s %(levelname)s:%(message)s')
logger = logging.getLogger(__name__)


@dataclass
class Config:
    username: str = ''
    password: str = ''

    def from_json(self):
        if config_file_path.is_file():
            with open('config.json', 'r') as config_file:
                configuration = json.load(config_file)
                self.username = configuration['username']
                self.password = configuration['password']


class UpdateDns:
    config = Config()
    args = None

    def __init__(self):
        self._arg_parsing()
        self._load_config()
        self._get_domains()
        self.domain_parts = self.args.domains.split('.')
        self.domain = '.'.join(self.domain_parts[-3:-1])
        if self.domain not in self.domain_list:
            logger.error("Domain '%s' not in list of available domains", self.domain)
            sys.exit(1)

    def _arg_parsing(self):
        valid_commands = ['present', 'cleanup', 'timeout']
        parser = argparse.ArgumentParser()
        parser.add_argument('command', choices=valid_commands, help=f'one of {",".join(valid_commands)}')
        parser.add_argument('domains', help='domains to update', nargs='?')
        parser.add_argument('token', help='token to set', nargs='?')
        self.args = parser.parse_args()
        logger.info("command is '%s'", self.args.command)
        logger.info("domains to update '%s'", self.args.domains)
        logger.info("token is '%s'", self.args.token)

    def _load_config(self):
        self.config.from_json()

    def _get_domains(self, selector='*'):
        data = tostring(
            E.request(
                E.auth(
                    E.user(self.config.username),
                    E.password(self.config.password),
                    E.context('10')
                ),
                E.task(
                    E.code('0105'),
                    E.view(
                        E.offset('0'),
                        E.limit('100')
                    ),
                    E.where(
                        E.key('name'),
                        E.operator('like'),
                        E.value(selector)
                    ),
                    E.key('created')
                )
            ), pretty_print=True, xml_declaration=True, encoding='UTF-8')

        response = requests.post(SCHLUND_XML_URL, data=data)
        tree = fromstring(response.content)
        names = tree.xpath('/response/result/data/domain/name')
        self.domain_list = []
        for name in names:
            self.domain_list.append(name.text)
        logger.debug("available domains: %s", self.domain_list)

    def update_request(self):
        request = E.request(
            E.auth(
                E.user(self.config.username),
                E.password(self.config.password),
                E.context('10')
            ),
            E.task(
                E.code('0202001'),
                E.default(
                    E.rr_rem(
                        E.name('.'.join(self.domain_parts[0:-3])),
                        E.type('TXT'),
                    ),
                    E.rr_add(
                        E.name('.'.join(self.domain_parts[0:-3])),
                        E.type('TXT'),
                        E.value(self.args.token)
                    )
                ),
                E.zone(
                    E.name(self.domain)
                )
            )
        )

        data = tostring(request, pretty_print=True, xml_declaration=True, encoding='UTF-8')
        return data

    def cleanup_request(self):
        request = E.request(
            E.auth(
                E.user(self.config.username),
                E.password(self.config.password),
                E.context('10')
            ),
            E.task(
                E.code('0202001'),
                E.default(
                    E.rr_rem(
                        E.name('.'.join(self.domain_parts[0:-3])),
                        E.type('TXT'),
                    )
                ),
                E.zone(
                    E.name(self.domain)
                )
            )
        )

        data = tostring(request, pretty_print=True, xml_declaration=True, encoding='UTF-8')
        return data

    def send_request_to_log(self):
        logger.info((self.update_request().decode("utf-8")))

    def send_update_xml(self):
        response = requests.post(SCHLUND_XML_URL, data=self.update_request())
        logger.info(response.content.decode("utf-8"))

    def send_cleanup_xml(self):
        response = requests.post(SCHLUND_XML_URL, data=self.cleanup_request())
        logger.info(response.content.decode("utf-8"))


if __name__ == '__main__':
    update_dns = UpdateDns()
    if update_dns.args.command is 'timeout':
        print({"timeout": 500, "interval": 30})
    elif update_dns.args.command is 'present':
        update_dns.send_update_xml()
    elif update_dns.args.command is 'present':
        update_dns.send_cleanup_xml()
    sys.exit()
