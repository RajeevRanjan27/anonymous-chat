# 🐛 Python 3.13 Compatibility Fix

## The Issue
Render is using **Python 3.13.4** by default, but **gevent doesn't compile** with Python 3.13 due to Cython compatibility issues.

## ✅ Fixed Approach
I've removed the problematic gevent dependencies and simplified the setup:

### Changes Made:
1. **Removed gevent** and gevent-websocket from requirements.txt
2. **Kept eventlet** which works better with Python 3.13
3. **Removed runtime.txt** to use Render's default Python 3.13.4
4. **Kept eventlet worker** in Procfile

## 🚀 Deploy Options

### Option 1: Eventlet Worker (Try This First)
**Start Command in Render:**
```
gunicorn --worker-class eventlet -w 1 app:app
```

### Option 2: Simple Python (If Option 1 Fails)
**Start Command in Render:**
```
python app.py
```

## 🔄 Updated Files:
- ✅ `requirements.txt` - Removed gevent, kept eventlet 0.35.2
- ✅ `Procfile` - Uses eventlet worker
- ✅ Removed `runtime.txt` - Let Render use Python 3.13.4
- ✅ Created `Procfile.simple` - Alternative approach

## 📝 If Eventlet Still Fails:
If eventlet still has issues with Python 3.13, try these alternatives:

### Alternative 1: Use threading worker
```
gunicorn --worker-class gthread --workers 1 --worker-connections 1000 app:app
```

### Alternative 2: Direct Flask (Development)
```
python app.py
```

## ✅ Expected Success
After this fix, you should see:
```
🔗 Anonymous Chat Server Starting...
Features:
- Temporary chat rooms with shareable links
- Automatic data deletion after 30 minutes of inactivity
- No persistent storage - all data wiped on server restart
- Anonymous participants
- Running on port [PORT]
```

The WebSockets will work through Flask-SocketIO's fallback mechanisms even without specialized async workers!
