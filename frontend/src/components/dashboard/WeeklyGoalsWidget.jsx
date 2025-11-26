import {
  Paper,
  Typography,
  Box,
  LinearProgress,
  Grid,
} from '@mui/material';
import { TrendingUp, Email } from '@mui/icons-material';

const WeeklyGoalsWidget = ({ goals }) => {
  const applicationsPercentage = goals?.applications_goal
    ? (goals.applications_current / goals.applications_goal) * 100
    : 0;

  const outreachPercentage = goals?.outreach_goal
    ? (goals.outreach_current / goals.outreach_goal) * 100
    : 0;

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Weekly Goals
      </Typography>
      <Typography variant="body2" color="text.secondary" gutterBottom>
        {goals?.days_remaining} days remaining this week
      </Typography>

      <Grid container spacing={3} sx={{ mt: 1 }}>
        <Grid item xs={12}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <TrendingUp sx={{ mr: 1, color: 'primary.main' }} />
            <Typography variant="body2">Applications</Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <Typography variant="h6" sx={{ mr: 1 }}>
              {goals?.applications_current || 0} / {goals?.applications_goal || 0}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              ({Math.round(applicationsPercentage)}%)
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={Math.min(applicationsPercentage, 100)}
            sx={{ height: 8, borderRadius: 4 }}
          />
        </Grid>

        <Grid item xs={12}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <Email sx={{ mr: 1, color: 'secondary.main' }} />
            <Typography variant="body2">Outreach</Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <Typography variant="h6" sx={{ mr: 1 }}>
              {goals?.outreach_current || 0} / {goals?.outreach_goal || 0}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              ({Math.round(outreachPercentage)}%)
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={Math.min(outreachPercentage, 100)}
            color="secondary"
            sx={{ height: 8, borderRadius: 4 }}
          />
        </Grid>
      </Grid>
    </Paper>
  );
};

export default WeeklyGoalsWidget;