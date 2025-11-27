
import {
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Box,
  Typography,
  Chip,
} from '@mui/material';
import {
  CheckCircle,
  Delete,
  Notifications,
  EmojiEvents,
  TrendingUp,
  Email,
} from '@mui/icons-material';
import { timeAgo } from '../../utils/helpers';

const ICON_MAP = {
  follow_up: <Email />,
  goal_reminder: <TrendingUp />,
  micro_quest: <EmojiEvents />,
  motivation: <Notifications />,
  system: <Notifications />,
};

const NotificationItem = ({ notification, onMarkRead, onDelete }) => {
  return (
    <ListItem
      sx={{
        bgcolor: notification.is_read ? 'transparent' : 'action.hover',
        borderRadius: 1,
        mb: 1,
      }}
    >
      {/* Left: Notification Icon */}
      <Box sx={{ mr: 2, color: 'primary.main' }}>
        {ICON_MAP[notification.type] || <Notifications />}
      </Box>

      {/* Middle: Title + Message */}
      <ListItemText
        primary={
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography variant="subtitle2">{notification.title}</Typography>

            {!notification.is_read && (
              <Chip label="New" size="small" color="primary" />
            )}
          </Box>
        }
        secondary={
          <Box>
            <Typography variant="body2" color="text.secondary">
              {notification.message}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {timeAgo(notification.created_at)}
            </Typography>
          </Box>
        }
      />

      {/* Right: Actions */}
      <ListItemSecondaryAction>
        <Box>
          {!notification.is_read && (
            <IconButton
              size="small"
              onClick={() => onMarkRead(notification.id)}
              title="Mark as read"
            >
              <CheckCircle fontSize="small" />
            </IconButton>
          )}

          <IconButton
            size="small"
            onClick={() => onDelete(notification.id)}
            color="error"
            title="Delete"
          >
            <Delete fontSize="small" />
          </IconButton>
        </Box>
      </ListItemSecondaryAction>
    </ListItem>
  );
};

export default NotificationItem;
