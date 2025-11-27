import { Paper, Typography, Box, List, ListItem, ListItemText, Avatar } from '@mui/material';
import {
  Work,
  Business,
  Description,
  CheckCircle,
  TrendingUp,
} from '@mui/icons-material';
import { formatDate } from '../../utils/helpers';

const ActivityFeedWidget = ({ applications }) => {
  const getActivityIcon = (type) => {
    const icons = {
      application: <Work />,
      company: <Business />,
      cv: <Description />,
      quest: <CheckCircle />,
      goal: <TrendingUp />,
    };
    return icons[type] || <Work />;
  };

  // Generate recent activity from applications
  const activities = applications
    ?.slice(0, 5)
    .map((app) => ({
      type: 'application',
      message: `Added: ${app.job_title} at ${app.company_name}`,
      date: app.created_at || app.applied_date,
      icon: <Work />,
    })) || [];

  return (
    <Paper sx={{ p: 2.5, height: '100%', display: 'flex', flexDirection: 'column', flex: 1 }}>
      <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, mb: 2 }}>
        Recent Activity
      </Typography>
      {activities.length === 0 ? (
        <Box sx={{ flexGrow: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', textAlign: 'center', p: 3 }}>
          <Box>
            <Work sx={{ fontSize: 48, color: 'text.secondary', opacity: 0.3, mb: 2 }} />
            <Typography variant="body2" color="text.secondary">
              No recent activity
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Start by adding your first application!
            </Typography>
          </Box>
        </Box>
      ) : (
        <List sx={{ flexGrow: 1, overflow: 'auto', pr: 1 }}>
          {activities.map((activity, index) => (
            <ListItem
              key={index}
              disablePadding
              sx={{
                py: 1.5,
                mb: 1.5,
                borderLeft: '3px solid',
                borderLeftColor: 'primary.main',
                pl: 2,
                bgcolor: 'action.hover',
                borderRadius: 1,
                transition: 'all 0.2s',
                '&:hover': {
                  bgcolor: 'action.selected',
                  transform: 'translateX(4px)',
                },
              }}
            >
              <Avatar
                sx={{
                  width: 36,
                  height: 36,
                  bgcolor: 'primary.light',
                  color: 'primary.main',
                  mr: 2,
                }}
              >
                {getActivityIcon(activity.type)}
              </Avatar>
              <ListItemText
                primary={activity.message}
                secondary={formatDate(activity.date)}
                primaryTypographyProps={{ variant: 'body2', fontWeight: 500, sx: { mb: 0.5 } }}
                secondaryTypographyProps={{ variant: 'caption' }}
              />
            </ListItem>
          ))}
        </List>
      )}
    </Paper>
  );
};

export default ActivityFeedWidget;

