import { Box, Typography, Button } from '@mui/material';
import {
  EmojiEvents as TrophyIcon,
  Dashboard as DashboardIcon,
} from '@mui/icons-material';

const Step7Celebration = ({ onComplete }) => {
  return (
    <Box sx={{ textAlign: 'center', py: 4 }}>
      <TrophyIcon sx={{ fontSize: 100, color: 'primary.main', mb: 3 }} />
      <Typography variant="h4" gutterBottom>
        You're All Set! 🎉
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4, maxWidth: 600, mx: 'auto' }}>
        Welcome to JobBuddy! Your personalized job search dashboard is ready. Let's
        start tracking applications, connecting with companies, and landing your dream
        job!
      </Typography>

      <Button
        variant="contained"
        size="large"
        startIcon={<DashboardIcon />}
        onClick={onComplete}
      >
        Go to Dashboard
      </Button>
    </Box>
  );
};

export default Step7Celebration;