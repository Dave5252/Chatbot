import time
import requests
from collections import defaultdict  # The defaultdict is a subdivision of the dict class. Its importance lies in the
# fact that it allows each new key to be given a default value based on the type of dictionary being created

from main import msgP
from LoadData import graph, WDT, WD, images

url = 'https://speakeasy.ifi.uzh.ch'


class Server:

    def __init__(self, username, password, url='https://speakeasy.ifi.uzh.ch'):
        self.agent_details = self.login(username, password)
        self._url = url
        self.password = password
        self.username = username
        self.session_token = self.agent_details['sessionToken']
        self.chat_state = defaultdict(lambda: {'messages': defaultdict(dict), 'initiated': False, 'my_alias': None})

    def listen(self):
        listen_freq = 1.5  # seconds
        while True:
            # check for all chatrooms
            current_rooms = self.check_rooms(session_token=self.session_token)['rooms']
            for room in current_rooms:
                # ignore finished conversations
                if room['remainingTime'] > 0:
                    room_id = room['uid']
                    if not self.chat_state[room_id]['initiated']:
                        # send a welcome message and get the alias of the agent in the chatroom
                        self.post_message(room_id=room_id, session_token=self.session_token,
                                          message='Whats up withit, after you sent me a meesage you need to be paicent for a few seconds, you know the WIFI at the UZH is not the best ;)'.format(
                                              listen_freq))
                        self.chat_state[room_id]['initiated'] = True
                        self.chat_state[room_id]['my_alias'] = room['alias']

                    # check for all messages
                    all_messages = self.check_room_state(room_id=room_id, since=0, session_token=self.session_token)[
                        'messages']

                    # you can also use ["reactions"] to get the reactions of the messages: STAR, THUMBS_UP, THUMBS_DOWN

                    for message in all_messages:
                        if message['authorAlias'] != self.chat_state[room_id]['my_alias']:

                            # check if the message is new
                            if message['ordinal'] not in self.chat_state[room_id]['messages']:
                                self.chat_state[room_id]['messages'][message['ordinal']] = message
                                print(
                                    '\t- Chatroom {} - new message #{}: \'{}\' - {}'.format(room_id, message['ordinal'],
                                                                                            message['message'],
                                                                                            self.get_time()))
                                start = time.time()
                                msgp = msgP(message["message"])
                                response = msgp.parseMsg(graph, WDT, WD, images)
                                end = time.time()
                                if end - start > 5:
                                    # send excuse message if the response takes too long
                                    response = response.replace("Hi, t", "T")
                                    excuse = "Sorry, I am a bit slow, I am still learning:) \n"
                                    response = excuse + response
                                self.post_message(room_id=room_id, session_token=self.session_token,
                                                  message=response)
            time.sleep(listen_freq)

    # check for available rooms -->https://speakeasy.ifi.uzh.ch/client-swagger#/Chat/getApiRooms
    def login(self, username: str, password: str):
        agent_details = requests.post(url=url + "/api/login", json={"username": username, "password": password}).json()
        print('- User {} successfully logged in with session \'{}\'!'.format(agent_details['userDetails']['username'],
                                                                             agent_details['sessionToken']))
        return agent_details

    def check_rooms(self, session_token: str):
        return requests.get(url=url + "/api/rooms", params={"session": session_token}).json()

    def check_room_state(self, room_id: str, since: int, session_token: str):
        return requests.get(url=url + "/api/room/{}/{}".format(room_id, since),
                            params={"roomId": room_id, "since": since, "session": session_token}).json()

    def post_message(self, room_id: str, session_token: str, message: str):
        tmp_des = requests.post(url=url + "/api/room/{}".format(room_id),
                                params={"roomId": room_id, "session": session_token},
                                data=message.encode('utf-8')).json()
        if tmp_des['description'] != 'Message received':
            print('\t\t Error: failed to post message: {}'.format(message))

    def get_time(self):
        return time.strftime("%H:%M:%S, %d-%m-%Y", time.localtime())

    def logout(self):
        if requests.get(url=url + "/api/logout", params={"session": self.session_token}).json()[
            'description'] == 'Logged out':
            print('- Session \'{}\' successfully logged out!'.format(self.session_token))


if __name__ == '__main__':
    username = 'david.diener_bot'
    password = 'czLFGXbrspCK0Q'
    demobot = Server(username, password)
    demobot.listen()
