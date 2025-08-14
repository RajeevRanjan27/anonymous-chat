# 🔗 Anonymous Chat App

A secure, temporary, and completely anonymous chat application that allows users to create temporary chat rooms with shareable links. All data is automatically deleted after 30 minutes of inactivity, ensuring complete privacy.

## 🛡️ Privacy & Security Features

- **Complete Anonymity**: No registration required, no tracking, no user profiling
- **Temporary Data**: All messages are deleted after 30 minutes of inactivity
- **No Persistent Storage**: Messages are only stored in memory and wiped when server restarts
- **Shareable Links**: Randomly generated shareable links that expire automatically
- **Real-time Communication**: Instant messaging using WebSocket technology
- **Secure Sessions**: Each user gets a unique temporary session ID

## 🚀 How to Run

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the Server**:
   ```bash
   python app.py
   ```

3. **Open in Browser**:
   Navigate to `http://localhost:5000` or `http://127.0.0.1:5000`

## 📱 How to Use

### Creating a Room
1. Click "Create Shareable Link"
2. Enter your display name (optional - defaults to "Anonymous")
3. Click "Generate Shareable Link"
4. Copy and share the generated link with others
5. Click "Join Chat Room" to enter your own room
6. Start chatting!

### Joining via Shared Link
1. Click on the shared link (format: `http://yourserver.com/chat/ROOMID`)
2. Enter your display name (optional - defaults to "Anonymous")
3. Click "Join Chat Room"
4. Start chatting!

### Chatting
- Type messages in the input field and press Enter or click Send
- See real-time messages from all participants
- View participant count in the header
- Leave room at any time using the "Leave Room" button

## 🔧 Technical Features

### Backend (Flask + SocketIO)
- **Real-time Communication**: WebSocket support for instant messaging
- **Room Management**: Create, join, and manage temporary chat rooms
- **Automatic Cleanup**: Background thread removes expired rooms every minute
- **Session Management**: Temporary user sessions with unique IDs
- **Error Handling**: Comprehensive error handling and validation

### Frontend (HTML + CSS + JavaScript)
- **Responsive Design**: Works on desktop and mobile devices
- **Modern UI**: Glass-morphism design with gradient backgrounds
- **Real-time Updates**: Live message display and user notifications
- **Keyboard Shortcuts**: Enter key support for sending messages
- **Visual Feedback**: Animations and hover effects

### Security Measures
- **No Data Persistence**: All data stored in memory only
- **Session Expiry**: 30-minute automatic room cleanup
- **Input Validation**: Message length limits and code validation
- **XSS Protection**: HTML escaping for all user inputs
- **Random Session IDs**: Cryptographically secure session generation

## 🌐 Network Access

The app runs on `0.0.0.0:5000` by default, meaning:
- **Local Access**: `http://localhost:5000`
- **Network Access**: `http://[your-ip]:5000` (accessible to others on same network)
- **Port**: Default port 5000 (configurable in app.py)

## 📂 File Structure

```
apps/
├── app.py                 # Main Flask application
├── templates/
│   └── index.html         # Frontend HTML template
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🔄 Data Lifecycle

1. **Room Creation**: User creates room → Server generates unique room ID → Shareable link created → Room stored in memory
2. **User Joins**: Users access via link → Temporary user sessions created
3. **Messaging**: Real-time message exchange → Messages stored in room history
4. **Cleanup**: After 30 minutes of inactivity → Room and all data automatically deleted

## ⚠️ Important Notes

- **No Data Recovery**: Once a room expires or server restarts, all messages are permanently lost
- **Memory Usage**: All data is stored in RAM - suitable for small to medium groups
- **Network Firewall**: Make sure port 5000 is open if sharing across networks
- **Browser Compatibility**: Modern browsers with WebSocket support required

## 🛠️ Customization

You can modify these settings in `app.py`:
- `ROOM_EXPIRY_MINUTES`: Change room expiry time (default: 30 minutes)
- `GRID_SIZE`: Change room code length (default: 6 characters)
- Port number in the final `socketio.run()` call (default: 5000)

## 🐛 Troubleshooting

- **Connection Issues**: Check if port 5000 is available and not blocked by firewall
- **Room Not Found**: Shared links expire after 30 minutes of inactivity
- **Invalid Link**: Make sure you're using the complete shareable link format
- **Messages Not Sending**: Check browser console for WebSocket connection errors
- **Link Sharing**: Share the complete URL including the `/chat/ROOMID` part

## 📄 License

This project is created for educational and privacy-focused communication purposes. Feel free to modify and use as needed.
