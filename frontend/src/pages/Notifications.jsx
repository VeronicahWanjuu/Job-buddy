import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  Button,
  ButtonGroup,
  IconButton,
  Chip,
} from '@mui/material';
import { toast } from 'react-toastify';
import api from '../api/axios';
import DeleteIcon from '@mui/icons-material/Delete';
import MarkEmailReadIcon from '@mui/icons-material/MarkEmailRead';
import MarkEmailUnreadIcon from '@mui/icons-material/MarkEmailUnread';

const Notifications = () => {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterUnread, setFilterUnread] = useState(false);

  useEffect(() => {
    fetchNotifications();
  }, [filterUnread]);

  const fetchNotifications = async () => {
    setLoading(true);
    try {
      const endpoint = filterUnread ? '/notifications?unread=true' : '/notifications';
      const response = await api.get(endpoint);
      setNotifications(response.data.notifications);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to fetch notifications.');
    } finally {
      setLoading(false);
    }
  };

  const handleMarkAsRead = async (id) => {
    try {
      await api.put(`/notifications/${id}/read`);
      toast.success('Notification marked as read.');
      fetchNotifications();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to mark notification as read.');
    }
  };

  const handleMarkAllAsRead = async () => {
    try {
      await api.put('/notifications/read-all');
      toast.success('All notifications marked as read.');
      fetchNotifications();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to mark all notifications as read.');
    }
  };

  const handleDeleteNotification = async (id) => {
    if (window.confirm('Are you sure you want to delete this notification?')) {
      try {
        await api.delete(`/notifications/${id}`);
        toast.success('Notification deleted.');
        fetchNotifications();
      } catch (error) {
        toast.error(error.response?.data?.error || 'Failed to delete notification.');
      }
    }
  };

  const handleClearAllNotifications = async () => {
    if (window.confirm('Are you sure you want to delete ALL notifications? This cannot be undone.')) {
      try {
        await api.delete('/notifications/clear-all');
        toast.success('All notifications cleared.');
        fetchNotifications();
      } catch (error) {
        toast.error(error.response?.data?.error || 'Failed to clear all notifications.');
      }
    }
  };

  const getNotificationChipColor = (type) => {
    switch (type) {
      case 'follow_up':
        return 'primary';
      case 'goal_reminder':
        return 'secondary';
      case 'micro_quest':
        return 'success';
      case 'motivation':
        return 'info';
      case 'system':
        return 'warning';
      default:
        return 'default';
    }
  };

  const groupNotificationsByDate = (notifs) => {
    const grouped = {};
    notifs.forEach(notif => {
      const date = new Date(notif.created_at).toLocaleDateString(undefined, {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      });
      if (!grouped[date]) {
        grouped[date] = [];
      }
      grouped[date].push(notif);
    });
    return grouped;
  };

  const groupedNotifications = groupNotificationsByDate(notifications);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="md">
      <Typography variant="h4" component="h1" gutterBottom>
        Notifications
      </Typography>

      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <ButtonGroup variant="contained" aria-label="notification filter buttons">
          <Button onClick={() => setFilterUnread(false)} disabled={!filterUnread}>
            All
          </Button>
          <Button onClick={() => setFilterUnread(true)} disabled={filterUnread}>
            Unread
          </Button>
        </ButtonGroup>
        <ButtonGroup variant="outlined" aria-label="notification actions buttons">
          <Button startIcon={<MarkEmailReadIcon />} onClick={handleMarkAllAsRead}>
            Mark All Read
          </Button>
          <Button startIcon={<DeleteIcon />} color="error" onClick={handleClearAllNotifications}>
            Clear All
          </Button>
        </ButtonGroup>
      </Box>

      {Object.keys(groupedNotifications).length > 0 ? (
        Object.keys(groupedNotifications).sort((a, b) => new Date(b) - new Date(a)).map(date => (
          <Box key={date} sx={{ mb: 4 }}>
            <Typography variant="h6" sx={{ mb: 2, borderBottom: 1, borderColor: 'divider', pb: 1 }}>
              {date}
            </Typography>
            <List>
              {groupedNotifications[date].map((notif) => (
                <ListItem
                  key={notif.id}
                  sx={{
                    bgcolor: notif.is_read ? 'background.paper' : 'primary.light',
                    mb: 1,
                    borderRadius: 1,
                    boxShadow: 1,
                  }}
                  secondaryAction={
                    <Box>
                      {!notif.is_read && (
                        <IconButton edge="end" aria-label="mark as read" onClick={() => handleMarkAsRead(notif.id)}>
                          <MarkEmailReadIcon />
                        </IconButton>
                      )}
                      <IconButton edge="end" aria-label="delete" onClick={() => handleDeleteNotification(notif.id)}>
                        <DeleteIcon />
                      </IconButton>
                    </Box>
                  }
                >
                  <ListItemText
                    primary={
                      <Box display="flex" alignItems="center">
                        <Chip
                          label={notif.type.replace(/_/g, ' ').toUpperCase()}
                          size="small"
                          color={getNotificationChipColor(notif.type)}
                          sx={{ mr: 1 }}
                        />
                        <Typography variant="subtitle1" fontWeight={notif.is_read ? 'normal' : 'bold'}>
                          {notif.title}
                        </Typography>
                      </Box>
                    }
                    secondary={notif.message}
                  />
                </ListItem>
              ))}
            </List>
          </Box>
        ))
      ) : (
        <Typography>No notifications found.</Typography>
      )}
    </Container>
  );
};

export default Notifications;