#Lemur-chat


This Flask-powered  Chat Application enables multiple users to communicate in chatrooms. It leverages WebSocket technology provided by Pusher for real-time bidirectional event-based communication.

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
    app_id='1699312',
    key='4f6a30582d3fee132dc9',
    secret='5a9abd70a7af2505b828',
    cluster='eu',
    ssl=True
)
```
