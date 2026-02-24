# Notification System - Quick Start Guide for Frontend

## 🚀 Quick Overview

**Base URL:** `http://localhost:8000/api/`  
**Auth:** All endpoints require JWT token in header: `Authorization: Bearer <token>`

---

## 📋 Essential Endpoints

### Get Notifications
```http
GET /api/notifications/
```
Returns paginated list of all notifications for current user.

### Get Unread Count
```http
GET /api/notifications/unread/
```
Returns only unread notifications (for badge count).

### Mark as Read
```http
POST /api/notifications/{id}/mark_read/
```
Marks single notification as read.

### Mark All Read
```http
POST /api/notifications/mark_all_as_read/
```
Marks all notifications as read.

### Get User Preferences
```http
GET /api/notification-preferences/settings/
```
Returns user's notification preferences.

### Update Preferences
```http
PUT /api/notification-preferences/{id}/update_preferences/
```
Updates notification preferences.

---

## 💡 Quick Implementation (React)

### 1. Create Notification Service
```javascript
// services/notificationService.js
const API_BASE = 'http://localhost:8000/api';

export const notificationService = {
  // Get all notifications
  getAll: async (token) => {
    const response = await fetch(`${API_BASE}/notifications/`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    return response.json();
  },

  // Get unread count
  getUnreadCount: async (token) => {
    const response = await fetch(`${API_BASE}/notifications/unread/`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    const data = await response.json();
    return data.count;
  },

  // Mark as read
  markAsRead: async (token, notificationId) => {
    await fetch(`${API_BASE}/notifications/${notificationId}/mark_read/`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` }
    });
  },

  // Mark all as read
  markAllAsRead: async (token) => {
    await fetch(`${API_BASE}/notifications/mark_all_as_read/`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` }
    });
  },

  // Get preferences
  getPreferences: async (token) => {
    const response = await fetch(`${API_BASE}/notification-preferences/settings/`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    return response.json();
  },

  // Update preferences
  updatePreferences: async (token, preferenceId, data) => {
    const response = await fetch(`${API_BASE}/notification-preferences/${preferenceId}/update_preferences/`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    });
    return response.json();
  }
};
```

### 2. Notification Bell Component
```jsx
// components/NotificationBell.jsx
import React, { useState, useEffect } from 'react';
import { notificationService } from '../services/notificationService';

function NotificationBell({ token }) {
  const [unreadCount, setUnreadCount] = useState(0);
  const [notifications, setNotifications] = useState([]);
  const [isOpen, setIsOpen] = useState(false);

  // Fetch notifications on mount and every 30 seconds
  useEffect(() => {
    fetchNotifications();
    const interval = setInterval(fetchNotifications, 30000);
    return () => clearInterval(interval);
  }, [token]);

  const fetchNotifications = async () => {
    try {
      const data = await notificationService.getAll(token);
      setNotifications(data.results || []);
      setUnreadCount(data.results.filter(n => !n.is_read).length);
    } catch (error) {
      console.error('Error fetching notifications:', error);
    }
  };

  const handleMarkAsRead = async (id) => {
    try {
      await notificationService.markAsRead(token, id);
      fetchNotifications();
    } catch (error) {
      console.error('Error marking as read:', error);
    }
  };

  const handleMarkAllAsRead = async () => {
    try {
      await notificationService.markAllAsRead(token);
      fetchNotifications();
    } catch (error) {
      console.error('Error marking all as read:', error);
    }
  };

  return (
    <div className="notification-bell">
      <button onClick={() => setIsOpen(!isOpen)} className="bell-icon">
        🔔
        {unreadCount > 0 && (
          <span className="badge">{unreadCount}</span>
        )}
      </button>

      {isOpen && (
        <div className="notification-dropdown">
          <div className="dropdown-header">
            <h3>Notifications</h3>
            {unreadCount > 0 && (
              <button onClick={handleMarkAllAsRead}>Mark all read</button>
            )}
          </div>

          <div className="notification-list">
            {notifications.length === 0 ? (
              <p>No notifications</p>
            ) : (
              notifications.map(notification => (
                <div
                  key={notification.id}
                  className={`notification-item ${!notification.is_read ? 'unread' : ''}`}
                  onClick={() => handleMarkAsRead(notification.id)}
                >
                  <div className="notification-icon">
                    {getNotificationIcon(notification.notification_type)}
                  </div>
                  <div className="notification-content">
                    <h4>{notification.subject}</h4>
                    <p>{notification.message}</p>
                    <span className="time">{formatTime(notification.created_at)}</span>
                  </div>
                </div>
              ))
            )}
          </div>

          <div className="dropdown-footer">
            <a href="/notifications">View all notifications</a>
          </div>
        </div>
      )}
    </div>
  );
}

// Helper functions
const getNotificationIcon = (type) => {
  const icons = {
    'result_published': '📊',
    'attendance_marked': '✓',
    'exam_scheduled': '📅',
    'enrollment_confirmed': '🎉',
    'grade_updated': '📝',
    'document_uploaded': '📎',
    'announcement': '📢',
    'system_alert': '⚠️'
  };
  return icons[type] || '🔔';
};

const formatTime = (dateString) => {
  const date = new Date(dateString);
  const now = new Date();
  const diff = now - date;
  
  if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
  return date.toLocaleDateString();
};

export default NotificationBell;
```

### 3. Notification Settings Page
```jsx
// pages/NotificationSettings.jsx
import React, { useState, useEffect } from 'react';
import { notificationService } from '../services/notificationService';

function NotificationSettings({ token }) {
  const [preferences, setPreferences] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadPreferences();
  }, []);

  const loadPreferences = async () => {
    try {
      const data = await notificationService.getPreferences(token);
      setPreferences(data);
    } catch (error) {
      console.error('Error loading preferences:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleToggle = async (field) => {
    const updated = { ...preferences, [field]: !preferences[field] };
    setPreferences(updated);
    
    try {
      await notificationService.updatePreferences(token, preferences.id, updated);
    } catch (error) {
      console.error('Error updating preferences:', error);
      // Revert on error
      setPreferences(preferences);
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div className="notification-settings">
      <h2>Notification Settings</h2>

      <div className="setting-group">
        <label>
          <input
            type="checkbox"
            checked={preferences.notifications_enabled}
            onChange={() => handleToggle('notifications_enabled')}
          />
          <span>Enable All Notifications</span>
        </label>
      </div>

      <h3>Notification Types</h3>
      <div className="setting-group">
        <label>
          <input
            type="checkbox"
            checked={preferences.result_published}
            onChange={() => handleToggle('result_published')}
            disabled={!preferences.notifications_enabled}
          />
          <span>📊 Result Published</span>
        </label>

        <label>
          <input
            type="checkbox"
            checked={preferences.attendance_marked}
            onChange={() => handleToggle('attendance_marked')}
            disabled={!preferences.notifications_enabled}
          />
          <span>✓ Attendance Marked</span>
        </label>

        <label>
          <input
            type="checkbox"
            checked={preferences.exam_scheduled}
            onChange={() => handleToggle('exam_scheduled')}
            disabled={!preferences.notifications_enabled}
          />
          <span>📅 Exam Scheduled</span>
        </label>

        <label>
          <input
            type="checkbox"
            checked={preferences.announcement}
            onChange={() => handleToggle('announcement')}
            disabled={!preferences.notifications_enabled}
          />
          <span>📢 Announcements</span>
        </label>
      </div>

      <h3>Advanced Options</h3>
      <div className="setting-group">
        <label>
          <input
            type="checkbox"
            checked={preferences.quiet_hours_enabled}
            onChange={() => handleToggle('quiet_hours_enabled')}
          />
          <span>Enable Quiet Hours</span>
        </label>

        {preferences.quiet_hours_enabled && (
          <div className="time-inputs">
            <label>
              From:
              <input type="time" value={preferences.quiet_hours_start || ''} />
            </label>
            <label>
              To:
              <input type="time" value={preferences.quiet_hours_end || ''} />
            </label>
          </div>
        )}
      </div>
    </div>
  );
}

export default NotificationSettings;
```

---

## 📱 Response Examples

### Notification Object
```json
{
  "id": 1,
  "notification_type": "result_published",
  "notification_type_display": "Result Published",
  "subject": "Your Exam Results Are Published",
  "message": "Your results for Mid Term Exam have been published.",
  "context": {
    "exam_name": "Mid Term Exam",
    "result_url": "/results/123",
    "percentage": 90.0
  },
  "is_read": false,
  "is_sent": true,
  "created_at": "2026-02-24T10:30:00Z"
}
```

### Preferences Object
```json
{
  "id": 1,
  "notifications_enabled": true,
  "result_published": true,
  "attendance_marked": true,
  "exam_scheduled": true,
  "enrollment_confirmed": true,
  "quiet_hours_enabled": false,
  "digest_enabled": false
}
```

---

## 🎨 Styling Tips

```css
/* Notification Bell */
.notification-bell {
  position: relative;
}

.bell-icon {
  font-size: 24px;
  background: none;
  border: none;
  cursor: pointer;
  position: relative;
}

.badge {
  position: absolute;
  top: -5px;
  right: -5px;
  background: #ff4444;
  color: white;
  border-radius: 10px;
  padding: 2px 6px;
  font-size: 12px;
  font-weight: bold;
}

/* Dropdown */
.notification-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  width: 400px;
  max-height: 500px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  z-index: 1000;
}

/* Unread notification */
.notification-item.unread {
  background: #f0f8ff;
  border-left: 3px solid #4dabf7;
}
```

---

## ✅ Checklist for Frontend Developer

- [ ] Set up notification service with API calls
- [ ] Create notification bell component with badge
- [ ] Implement dropdown with notification list
- [ ] Add mark as read functionality
- [ ] Create notification settings page
- [ ] Add polling (every 30 seconds) for new notifications
- [ ] Style unread vs read notifications differently
- [ ] Add notification icons based on type
- [ ] Implement "mark all as read" button
- [ ] Add time formatting (e.g., "5m ago", "2h ago")
- [ ] Handle empty state (no notifications)
- [ ] Add error handling for API calls
- [ ] Test with different notification types
- [ ] Add loading states
- [ ] Make responsive for mobile

---

## 🐛 Testing

1. **Get Token:** Login via `/api/token/` to get JWT token
2. **Test in Browser:** Visit `http://localhost:8000/api/notifications/` (DRF browsable API)
3. **Test with Postman:** Import endpoints and test with your token
4. **Test Preferences:** Update settings and verify changes persist

---

## 📞 Need Help?

- **Full Documentation:** See `NOTIFICATION_API_DOCS.md`
- **API Browser:** `http://localhost:8000/api/`
- **Backend Team:** Contact for any API issues

---

**Last Updated:** February 24, 2026  
**Version:** 1.0
