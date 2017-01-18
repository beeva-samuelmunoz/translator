# -*- coding: utf-8 -*-
# AUTHOR: Samuel M.H. <samuel.munoz@beeva.com>

"""Traduction library based on the Yandex service.

https://translate.yandex.com/
"""

"""
TODOS:
- raise exceptions. Decorator?
"""

__author__ = "Samuel M.H."
__email__ = "samuel.munoz@beeva.com"
__status__ = "Experimental"


import requests

class Yandex(object):

    _ENDPOINT = "https://translate.yandex.net/api/v1.5/tr.json"

    _RESPONSES = {
        200: "Operation completed successfully",
        401: "Invalid API key",
        402: "Blocked API key",
        404: "Exceeded the daily limit on the amount of translated text"
    }


    def __init__(self, key):
        self._KEY = key


    def list_languages(self, language='en', callback=''):
        '''
            DOC: https://tech.yandex.com/translate/doc/dg/reference/getLangs-docpage/
        '''
        response = requests.get(
            url=self._ENDPOINT+"/getLangs",
            params={
                "key": self._KEY,
                "ui": language,
                "callback": callback
            }
        )
        return response.json()


    def translate_iter(self, text_list, lang_from, lang_to, text_format="plain", options="", callback="", max_size=100000):
        '''
        Efficient translate in batches, not in one call.

        Parameters
        ----------
        max_size: int
            Maximum size of the batch (in characters).
        '''
        batch, batch_size = [], 0
        for txt in text_list:
            txt_size = len(txt)
            if (batch_size + txt_size) > max_size:
                for txt in self.translate(batch, lang_from, lang_to, text_format, options, callback):
                    yield txt
                #Reset batch
                batch, batch_size = [txt], txt_size
            else:
                batch.append(txt)
                batch_size += txt_size
        #Last batch
        for txt in self.translate(batch, lang_from, lang_to, text_format, options, callback):
            yield txt


    def translate(self, text_list, lang_from, lang_to, text_format="plain", options="", callback=""):
        '''
        Translate a text list.
        Documentation in:
          https://tech.yandex.com/translate/doc/dg/reference/translate-docpage/

        Parameters
        ----------
        text_list: [str]
            The texts to translate.
        lang_from: str
            Original language.
        lang_to: str
            Destination language.
        text_format: str
            "plain" or "html"
        options: str
            See official documentation.
        callback: str
            The name of the callback function. Use for getting a JSONP response.

        Returns
        -------
        _: [str]
            List of translated texts.
        '''
        response = requests.post(
            url=self._ENDPOINT+"/translate",
            params={
                "key": self._KEY,
                "text": text_list,
                "lang": lang_from+'-'+lang_to,
                "format": text_format,
                "options": options,
                "callback": callback
            }
        )
        if response.status_code==200:
            return response.json()['text']
        else:  # If fails, see: https://yandex.com/support/webmaster/indexing/http-codes.xml
            print "{} {}".format(response.status_code, response.reason)
            return [[]]*len(text_list)


    def detect_language(self, text, hint='', callback=''):
        response = requests.get(
            url=self._ENDPOINT+"/detect",
            params={
                "key": self._KEY,
                "text": text,
                "hint": hint,
                "callback": callback
            }
        )
        return response.json()
