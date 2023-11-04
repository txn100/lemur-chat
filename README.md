### lemur-chat

Lemur-chat started off as a dare: how fast could I build a functional app that we could communicate on? The answer is 3 hours. Lemur chat is a way for me and my friends to communicate but has a huge expansion potential. I am currently working on Lemur-Chat 2.0, aimed towards intra-organizational communication(like teams).

This Flask-powered  Chat Application enables multiple users to communicate in chatrooms. It leverages WebSocket technology provided by Pusher for real-time bidirectional event-based communication. 

## Link : http://lemur-chat.pacifictrout.com

Lemur Chat is not open to the public, and registrations have been turned off. This is documentation if you would like to fork this repo, to create your own private chat. I am using pythonanywhere as a hosting provider(would not recommend for such app)

## Features

- **User Authentication**: Secure login mechanism to ensure message privacy.
- **Real-time Messaging**: Leverages Pusher for live message broadcasting.
- **Multiple Chatrooms**: Support for different chat themes.
- **Message History**: Persistent storage of messages using an SQLite database.
- **Session Management**: Flask session-based user sessions for security and convenience.

## Getting Started

### Prerequisites

- Python 3.x
- Pip package manager
- Virtual Environment (recommended)

To use your own Pusher API key modify these following in terminalChat.py:

```
pusher = Pusher(
    app_id='xxxx',
    key='xxxx',
    secret='xxx',
    cluster='xx',
    ssl=xxxxx
)
```
