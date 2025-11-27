import { Paper, Typography, Box, Button, Grid } from '@mui/material';
import {
  Add,
  Business,
  Description,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

const QuickActionsWidget = () => {
  const navigate = useNavigate();

  const actions = [
    {
      icon: <Add />,
      title: 'Add Application',
      description: 'Track a new job application',
      onClick: () => navigate('/applications'),
      color: 'primary'
    },
    {
      icon: <Business />,
      title: 'Add Company',
      description: 'Add a target company to your list',
      onClick: () => navigate('/companies'),
      color: 'secondary'
    },
    {
      icon: <Description />,
      title: 'Analyze CV',
      description: 'Check your CV ATS score',
      onClick: () => navigate('/cv-matcher'),
      color: 'success'
    }
  ];

  return (
    <Paper sx={{ p: 2.5, height: '100%', display: 'flex', flexDirection: 'column', flex: 1 }}>
      <Typography variant="h6" gutterBottom sx={{ mb: 2, fontWeight: 600 }}>
        Quick Actions
      </Typography>
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5, flexGrow: 1 }}>
        {actions.map((action) => (
          <Button
            key={action.title}
            fullWidth
            variant="outlined"
            color={action.color}
            startIcon={action.icon}
            onClick={action.onClick}
            sx={{
              py: 2,
              px: 2,
              justifyContent: 'flex-start',
              textAlign: 'left',
              borderWidth: 2,
              '&:hover': {
                borderWidth: 2,
                transform: 'translateX(4px)',
                boxShadow: 3,
                bgcolor: `${action.color}.50`,
              },
              transition: 'all 0.2s ease',
            }}
          >
            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 0.5 }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                {action.title}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {action.description}
              </Typography>
            </Box>
          </Button>
        ))}
      </Box>
    </Paper>
  );
};

export default QuickActionsWidget;