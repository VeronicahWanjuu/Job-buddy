import { Paper, Typography, Box, Button, Grid } from '@mui/material';
import {
  Add,
  Business,
  Description,
  Email,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

const QuickActionsWidget = () => {
  const navigate = useNavigate();

  const actions = [
    {
      label: 'Add Application',
      icon: <Add />,
      color: 'primary',
      onClick: () => navigate('/applications'),
    },
    {
      label: 'Add Company',
      icon: <Business />,
      color: 'secondary',
      onClick: () => navigate('/companies'),
    },
    {
      label: 'Analyze CV',
      icon: <Description />,
      color: 'success',
      onClick: () => navigate('/cv-matcher'),
    },
    {
      label: 'Send Outreach',
      icon: <Email />,
      color: 'info',
      onClick: () => navigate('/companies'),
    },
  ];

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Quick Actions
      </Typography>
      <Grid container spacing={2} sx={{ mt: 1 }}>
        {actions.map((action) => (
          <Grid item xs={6} key={action.label}>
            <Button
              fullWidth
              variant="outlined"
              color={action.color}
              startIcon={action.icon}
              onClick={action.onClick}
              sx={{ py: 1.5 }}
            >
              {action.label}
            </Button>
          </Grid>
        ))}
      </Grid>
    </Paper>
  );
};

export default QuickActionsWidget;