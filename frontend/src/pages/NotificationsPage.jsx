import { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Button,
  List,
  Paper,
  ToggleButtonGroup,
  ToggleButton,
} from '@mui/material';
import { CheckCircleOutline, Delete } from '@mui/icons-material';
import { toast } from 'react-toastify';
import api from '../services/api';
import LoadingSpinner from '../components/common/LoadingSpinner';
import EmptyState from '../components/common/EmptyState';
import NotificationItem from '../components/notifications/NotificationItem';
import { formatDate } from '../utils/helpers';

const NotificationsPage = () => {
  const [loading, setLoading] = useState(true);
  const [notifications, setNotifications] = useState([]);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchNotifications();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filter]);

  const fetchNotifications = async () => {
    setLoading(true);
    try {
      const url = filter === 'unread' ? '/notifications?unread=true' : '/notifications';
      const response = await api.get(url);
      setNotifications(response.data.notifications);
    } catch (error) {
      toast.error('Failed to load notifications');
    } finally {
      setLoading(false);
    }
  };

  const handleMarkRead = async (notificationId) => {
    try {
      await api.put(`/notifications/${notificationId}/read`);
      fetchNotifications();
    } catch (error) {
      toast.error('Failed to mark notification as read');
    }
  };

  const handleDelete = async (notificationId) => {
    try {
      await api.delete(`/notifications/${notificationId}`);
      toast.success('Notification deleted');
      fetchNotifications();
    } catch (error) {
      toast.error('Failed to delete notification');
    }
  };

  const handleMarkAllRead = async () => {
    try {
      await api.put('/notifications/read-all');
      toast.success('All notifications marked as read');
      fetchNotifications();
    } catch (error) {
      toast.error('Failed to mark all as read');
    }
  };

  const handleClearAll = async () => {
    if (!window.confirm('Delete all notifications? This cannot be undone.')) {
      return;
    }

    try {
      await api.delete('/notifications/clear-all');
      toast.success('All notifications cleared');
      fetchNotifications();
    } catch (error) {
      toast.error('Failed to clear notifications');
    }
  };

  // Group notifications by date
  const groupedNotifications = notifications.reduce((groups, notification) => {
    const date = formatDate(notification.created_at);
    if (!groups[date]) {
      groups[date] = [];
    }
    groups[date].push(notification);
    return groups;
  }, {});

  if (loading) {
    return <LoadingSpinner message="Loading notifications..." />;
  }

  return (
    <Container maxWidth="md">
      <Typography variant="h4" gutterBottom>
        Notifications
      </Typography>

      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <ToggleButtonGroup
          value={filter}
          exclusive
          onChange={(e, value) => value && setFilter(value)}
          size="small"
        >
          <ToggleButton value="all">All</ToggleButton>
          <ToggleButton value="unread">Unread</ToggleButton>
        </ToggleButtonGroup>

        <Box>
          {notifications.length > 0 && (
            <>
              <Button
                size="small"
                startIcon={<CheckCircleOutline />}
                onClick={handleMarkAllRead}
                sx={{ mr: 1 }}
              >
                Mark All Read
              </Button>
              <Button
                size="small"
                startIcon={<Delete />}
                onClick={handleClearAll}
                color="error"
              >
                Clear All
              </Button>
            </>
          )}
        </Box>
      </Box>

      {notifications.length === 0 ? (
        <EmptyState
          title="No notifications"
          message={filter === 'unread' ? 'You have no unread notifications' : 'You have no notifications'}
        />
      ) : (
        Object.entries(groupedNotifications).map(([date, notifs]) => (
          <Paper key={date} sx={{ p: 2, mb: 2 }}>
            <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>
              {date}
            </Typography>
            <List disablePadding>
              {notifs.map((notification) => (
                <NotificationItem
                  key={notification.id}
                  notification={notification}
                  onMarkRead={handleMarkRead}
                  onDelete={handleDelete}
                />
              ))}
            </List>
          </Paper>
        ))
      )}
    </Container>
  );
};

export default NotificationsPage;