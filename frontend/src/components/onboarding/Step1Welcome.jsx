import { Box, Typography, Button } from '@mui/material';
import { EmojiEvents as TrophyIcon } from '@mui/icons-material';

const Step1Welcome = ({ onNext }) => {
  return (
    <Box sx={{ textAlign: 'center', py: 4 }}>
      <TrophyIcon sx={{ fontSize: 80, color: 'primary.main', mb: 3 }} />
      <Typography variant="h4" gutterBottom>
        Welcome to JobBuddy! 🎉
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4, maxWidth: 600, mx: 'auto' }}>
        We're excited to help you land your dream job! Let's get to know you better so we
        can personalize your experience and maximize your success.
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 4 }}>
        This will only take 2-3 minutes
      </Typography>
      <Button variant="contained" size="large" onClick={onNext}>
        Let's Get Started
      </Button>
    </Box>
  );
};

export default Step1Welcome;