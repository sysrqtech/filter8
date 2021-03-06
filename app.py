#!/usr/bin/env python3
# coding=utf-8

import os
import vk_api

import flask

app = flask.Flask(__name__)

GROUP_IDS = [int(gid.strip())
             for gid in os.environ.get("IDS", "0").split(',')]
CHECK_STRINGS = os.environ.get("CHECK_STRINGS", "").split(',')
TOKENS = os.environ.get("TOKENS", "").split(',')


class Community:
    def __init__(self, group_id: int, check_string, token):
        self.id: int = group_id
        self.check_string = check_string
        self.token = token

        self.api = vk_api.VkApi(token=self.token, api_version="5.80").get_api()

    def mark_important(self, peer_id):
        self.api.messages.markAsImportantConversation(peer_id=peer_id)


def get_community(event: dict):
    group_id = event["group_id"]
    index = GROUP_IDS.index(group_id)
    check_string = CHECK_STRINGS[index]
    token = TOKENS[index]
    return Community(group_id, check_string, token)


@app.route("/callback", methods=["POST"])
def callback():
    event: dict = flask.request.get_json()
    community: Community = get_community(event)

    event_type = event["type"]
    if event_type == "confirmation":
        return community.check_string
    if event_type == "message_new":
        message = event["object"]
        from_id = message["from_id"]
        is_important = message["important"]
        if from_id != -community.id and not is_important:
            peer_id = message["peer_id"]
            community.mark_important(peer_id)
    return "ok"


@app.route("/callback", methods=["GET"])
def howto():
    return flask.Markup("""
    1. Зайди в Настройки группы -> Работа с API -> Callback API<br>
    2. Вставь текущую ссылку в поле Адрес<br>
    3. Нажми Подтвердить<br>
    4. На вкладке Типы событий отметь Входящее сообщение<br>
    5. ????<br>
    6. PROFIT!<br><br>
    (по всем вопросам обращайтесь <a href="https://vk.me/cybertailor">к Сайберу</a>)
    """)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
