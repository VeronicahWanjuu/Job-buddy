import { Paper, Typography, Box } from '@mui/material';
import { WavingHand } from '@mui/icons-material';

const WelcomeWidget = ({ userName, dreamMilestone }) => {
  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  return (
    <Paper sx={{ p: 3, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <WavingHand sx={{ mr: 1, fontSize: 32 }} />
        <Typography variant="h5">
          {getGreeting()}, {userName}!
        </Typography>
      </Box>
      <Typography variant="body1" sx={{ opacity: 0.9 }}>
        Your goal: <strong>{dreamMilestone}</strong>
      </Typography>
      <Typography variant="body2" sx={{ mt: 1, opacity: 0.8 }}>
        Let's make today count! 💪
      </Typography>
    </Paper>
  );
};

export default WelcomeWidget;