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
    <Paper sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">Recent Applications</Typography>
        <Button
          size="small"
          endIcon={<ArrowForward />}
          onClick={() => navigate('/applications')}
        >
          View All
        </Button>
      </Box>

      {applications.length === 0 ? (
        <Box sx={{ textAlign: 'center', py: 3 }}>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            No applications yet
          </Typography>
          <Button
            variant="contained"
            size="small"
            startIcon={<Add />}
            onClick={() => navigate('/applications')}
            sx={{ mt: 1 }}
          >
            Add Your First Application
          </Button>
        </Box>
      ) : (
        <List>
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