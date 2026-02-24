# Notification System API Documentation

## Overview
The notification system provides real-time alerts for academic events including exam results, attendance, exam schedules, and enrollment confirmations. Users receive both in-app notifications and email alerts based on their preferences.

---

## Base URL
```
http://localhost:8000/api/
```

## Authentication
All endpoints require JWT authentication:
```http
Authorization: Bearer <your_jwt_token>
```

---

## API Endpoints

### 1. List Notifications

**GET** `/api/notifications/`

Get all notifications for the authenticated user.

**Query Parameters:**
- `page` (optional): Page number for pagination
- `ordering` (optional): Sort by fields (e.g., `-created_at`, `is_read`)

**Response:**
```json
{
  "count": 15,
  "next": "http://localhost:8000/api/notifications/?page=2",
  "previous": null,
  "results": [
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
      "sent_at": "2026-02-24T10:30:00Z",
      "created_at": "2026-02-24T10:30:00Z",
      "updated_at": "2026-02-24T10:30:00Z"
    }
  ]
}
```

---

### 2. Get Unread Notifications

**GET** `/api/notifications/unread/`

Get only unread notifications for the authenticated user.

**Response:**
```json
{
  "count": 5,
  "results": [
    {
      "id": 2,
      "notification_type": "attendance_marked",
      "subject": "Attendance Recorded",
      "message": "Your attendance for today has been marked.",
      "is_read": false,
      "created_at": "2026-02-24T09:00:00Z"
    }
  ]
}
```

---

### 3. Mark Notification as Read

**POST** `/api/notifications/{id}/mark_read/`

Mark a specific notification as read.

**Response:**
```json
{
  "status": "marked as read",
  "notification_id": 1
}
```

---

### 4. Mark All Notifications as Read

**POST** `/api/notifications/mark_all_as_read/`

Mark all notifications for the current user as read.

**Response:**
```json
{
  "status": "all notifications marked as read",
  "count": 5
}
```

---

### 5. Bulk Notification Actions

**POST** `/api/notifications/bulk_action/`

Perform bulk actions on multiple notifications.

**Request Body:**
```json
{
  "action": "mark_read",  // or "delete"
  "notification_ids": [1, 2, 3, 4, 5]
}
```

**Response:**
```json
{
  "status": "bulk action completed",
  "action": "mark_read",
  "count": 5
}
```

---

### 6. Get User Notification Preferences

**GET** `/api/notification-preferences/settings/`

Get notification preferences for the authenticated user.

**Response:**
```json
{
  "id": 1,
  "user": 1,
  "notifications_enabled": true,
  "result_published": true,
  "attendance_marked": true,
  "exam_scheduled": true,
  "enrollment_confirmed": true,
  "grade_updated": true,
  "document_uploaded": false,
  "announcement": true,
  "system_alert": true,
  "quiet_hours_enabled": false,
  "quiet_hours_start": null,
  "quiet_hours_end": null,
  "digest_enabled": false,
  "digest_time": "09:00:00",
  "created_at": "2026-01-15T08:00:00Z",
  "updated_at": "2026-02-20T14:30:00Z"
}
```

---

### 7. Update Notification Preferences

**PUT** `/api/notification-preferences/{id}/update_preferences/`

**PATCH** `/api/notification-preferences/{id}/update_preferences/`

Update user notification preferences.

**Request Body:**
```json
{
  "notifications_enabled": true,
  "result_published": true,
  "attendance_marked": false,
  "exam_scheduled": true,
  "quiet_hours_enabled": true,
  "quiet_hours_start": "22:00:00",
  "quiet_hours_end": "08:00:00",
  "digest_enabled": false
}
```

**Response:**
```json
{
  "status": "preferences updated",
  "notifications_enabled": true,
  "result_published": true,
  "attendance_marked": false,
  "exam_scheduled": true
}
```

---

## Notification Types

The system supports 8 notification types:

| Type | Value | Description |
|------|-------|-------------|
| Result Published | `result_published` | Exam results are available |
| Attendance Marked | `attendance_marked` | Daily attendance recorded |
| Exam Scheduled | `exam_scheduled` | New exam created |
| Enrollment Confirmed | `enrollment_confirmed` | Student enrolled in class |
| Grade Updated | `grade_updated` | Grades modified |
| Document Uploaded | `document_uploaded` | New documents available |
| Announcement | `announcement` | School announcements |
| System Alert | `system_alert` | Critical system messages |

---

## Implementation Examples

### React / JavaScript

#### 1. Fetch Notifications
```javascript
const fetchNotifications = async () => {
  try {
    const response = await fetch('http://localhost:8000/api/notifications/', {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    const data = await response.json();
    setNotifications(data.results);
    setUnreadCount(data.results.filter(n => !n.is_read).length);
  } catch (error) {
    console.error('Error fetching notifications:', error);
  }
};
```

#### 2. Mark as Read
```javascript
const markAsRead = async (notificationId) => {
  try {
    await fetch(`http://localhost:8000/api/notifications/${notificationId}/mark_read/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    // Refresh notifications
    fetchNotifications();
  } catch (error) {
    console.error('Error marking notification as read:', error);
  }
};
```

#### 3. Update Preferences
```javascript
const updatePreferences = async (preferences) => {
  try {
    const response = await fetch(
      `http://localhost:8000/api/notification-preferences/${preferenceId}/update_preferences/`,
      {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(preferences)
      }
    );
    const data = await response.json();
    console.log('Preferences updated:', data);
  } catch (error) {
    console.error('Error updating preferences:', error);
  }
};
```

#### 4. Poll for New Notifications
```javascript
// Poll every 30 seconds
useEffect(() => {
  const interval = setInterval(() => {
    fetchNotifications();
  }, 30000);
  
  return () => clearInterval(interval);
}, []);
```

---

### Vue.js Example

```vue
<template>
  <div class="notifications">
    <div class="notification-badge" v-if="unreadCount > 0">
      {{ unreadCount }}
    </div>
    <div v-for="notification in notifications" :key="notification.id">
      <div :class="['notification-item', { unread: !notification.is_read }]">
        <h4>{{ notification.subject }}</h4>
        <p>{{ notification.message }}</p>
        <button @click="markAsRead(notification.id)">Mark as Read</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      notifications: [],
      unreadCount: 0
    }
  },
  methods: {
    async fetchNotifications() {
      const response = await this.$http.get('/api/notifications/', {
        headers: { Authorization: `Bearer ${this.$store.state.token}` }
      });
      this.notifications = response.data.results;
      this.unreadCount = this.notifications.filter(n => !n.is_read).length;
    },
    async markAsRead(id) {
      await this.$http.post(`/api/notifications/${id}/mark_read/`, {}, {
        headers: { Authorization: `Bearer ${this.$store.state.token}` }
      });
      this.fetchNotifications();
    }
  },
  mounted() {
    this.fetchNotifications();
    // Poll every 30 seconds
    setInterval(this.fetchNotifications, 30000);
  }
}
</script>
```

---

### Flutter / Dart Example

```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

class NotificationService {
  final String baseUrl = 'http://localhost:8000/api';
  final String token;

  NotificationService(this.token);

  Future<List<Notification>> fetchNotifications() async {
    final response = await http.get(
      Uri.parse('$baseUrl/notifications/'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return (data['results'] as List)
          .map((json) => Notification.fromJson(json))
          .toList();
    } else {
      throw Exception('Failed to load notifications');
    }
  }

  Future<void> markAsRead(int notificationId) async {
    final response = await http.post(
      Uri.parse('$baseUrl/notifications/$notificationId/mark_read/'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode != 200) {
      throw Exception('Failed to mark notification as read');
    }
  }

  Future<Map<String, dynamic>> getPreferences() async {
    final response = await http.get(
      Uri.parse('$baseUrl/notification-preferences/settings/'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('Failed to load preferences');
    }
  }
}
```

---

## UI/UX Recommendations

### 1. Notification Bell Icon
```jsx
<div className="notification-bell">
  <BellIcon />
  {unreadCount > 0 && (
    <span className="badge">{unreadCount}</span>
  )}
</div>
```

### 2. Notification Dropdown
- Show latest 5-10 notifications
- "Mark all as read" button at top
- "View all" link at bottom
- Auto-refresh every 30 seconds

### 3. Notification Center Page
- Filter by type (Results, Attendance, Exams, etc.)
- Filter by read/unread
- Search functionality
- Bulk actions (select multiple, mark as read/delete)

### 4. Settings Page
```
[x] Enable Notifications
    [x] Result Published
    [x] Attendance Marked
    [x] Exam Scheduled
    [x] Enrollment Confirmed
    [ ] Grade Updated
    [ ] Document Uploaded
    [x] Announcements
    [x] System Alerts

[ ] Enable Quiet Hours
    From: [22:00] To: [08:00]

[ ] Enable Daily Digest
    Send at: [09:00]
```

---

## Real-time Updates (Optional Enhancement)

For real-time notifications without polling, consider:

### WebSocket Integration (Future)
```javascript
// Using Django Channels (to be implemented)
const ws = new WebSocket('ws://localhost:8000/ws/notifications/');

ws.onmessage = (event) => {
  const notification = JSON.parse(event.data);
  // Show toast notification
  showToast(notification.subject, notification.message);
  // Update notification list
  fetchNotifications();
};
```

### Push Notifications (Future)
- Firebase Cloud Messaging (FCM) for mobile
- Web Push API for browsers

---

## Error Handling

```javascript
const handleApiError = (error) => {
  if (error.response?.status === 401) {
    // Token expired, redirect to login
    window.location.href = '/login';
  } else if (error.response?.status === 403) {
    // No permission
    showError('You do not have permission to access this resource');
  } else if (error.response?.status === 404) {
    // Not found
    showError('Notification not found');
  } else {
    // Generic error
    showError('An error occurred. Please try again.');
  }
};
```

---

## Testing the API

### Using cURL

```bash
# Get notifications
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/notifications/

# Mark as read
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/notifications/1/mark_read/

# Update preferences
curl -X PUT \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"attendance_marked": false, "result_published": true}' \
  http://localhost:8000/api/notification-preferences/1/update_preferences/
```

### Using Postman
1. Create a new request
2. Set method (GET/POST/PUT)
3. Add header: `Authorization: Bearer YOUR_TOKEN`
4. For POST/PUT: Set body to JSON and add data
5. Send request

---

## API Browsable Interface

Visit: `http://localhost:8000/api/`

The Django REST Framework provides a browsable API where you can:
- Test endpoints directly in the browser
- See available fields and formats
- Submit test data
- View API documentation

---

## Contact

For questions or issues with the notification API, contact the backend team.

**API Version:** 1.0  
**Last Updated:** February 24, 2026
