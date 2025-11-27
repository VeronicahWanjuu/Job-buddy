import {
  Paper,
  Typography,
  Box,
  List,
  ListItem,
  ListItemText,
  Chip,
  Button,
} from '@mui/material';
import { Add, ArrowForward } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { formatDate } from '../../utils/helpers';
import { STATUS_COLORS } from '../../utils/constants';

const RecentApplicationsWidget = ({ applications }) => {
  const navigate = useNavigate();

  return (
    <Paper sx={{ p: 2, height: '100%', display: 'flex', flexDirection: 'column', maxHeight: 300 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6" sx={{ fontWeight: 600 }}>Recent Applications</Typography>
        <Button
          size="small"
          endIcon={<ArrowForward />}
          onClick={() => navigate('/applications')}
          variant="outlined"
        >
          View All
        </Button>
      </Box>

      {applications.length === 0 ? (
        <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center', py: 4 }}>
          <Box
            component="svg"
            sx={{
              width: 80,
              height: 80,
              mb: 2,
              opacity: 0.4,
              color: 'primary.main',
            }}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </Box>
          <Typography variant="body1" color="text.secondary" gutterBottom sx={{ fontWeight: 500 }}>
            No applications yet
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3, maxWidth: 300 }}>
            Start tracking your job applications to see them here
          </Typography>
          <Button
            variant="contained"
            size="medium"
            startIcon={<Add />}
            onClick={() => navigate('/applications')}
            sx={{ mt: 1 }}
          >
            Add Your First Application
          </Button>
        </Box>
      ) : (
        <List sx={{ flexGrow: 1, overflow: 'auto' }}>
          {applications.slice(0, 5).map((app) => (
            <ListItem key={app.id} divider>
              <ListItemText
                primary={app.job_title}
                secondary={`${app.company_name} • ${formatDate(app.created_at)}`}
              />
              <Chip
                label={app.status}
                size="small"
                sx={{
                  bgcolor: STATUS_COLORS[app.status],
                  color: 'white',
                }}
              />
            </ListItem>
          ))}
        </List>
      )}
    </Paper>
  );
};

export default RecentApplicationsWidget;