import { Paper, Typography, Box, Chip } from '@mui/material';
import { LocalFire, EmojiEvents, Star } from '@mui/icons-material';

const StreakWidget = ({ streak }) => {
  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Your Streak
      </Typography>

      <Box sx={{ textAlign: 'center', my: 3 }}>
        <LocalFire sx={{ fontSize: 64, color: 'orange' }} />
        <Typography variant="h3" component="div">
          {streak?.current_streak || 0}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Day Streak
        </Typography>
      </Box>

      <Box sx={{ display: 'flex', justifyContent: 'space-around', mt: 2 }}>
        <Box sx={{ textAlign: 'center' }}>
          <EmojiEvents sx={{ color: 'gold', mb: 0.5 }} />
          <Typography variant="body2" color="text.secondary">
            Best Streak
          </Typography>
          <Typography variant="h6">{streak?.longest_streak || 0}</Typography>
        </Box>

        <Box sx={{ textAlign: 'center' }}>
          <Star sx={{ color: 'primary.main', mb: 0.5 }} />
          <Typography variant="body2" color="text.secondary">
            Total Points
          </Typography>
          <Typography variant="h6">{streak?.total_points || 0}</Typography>
        </Box>
      </Box>

      <Box sx={{ mt: 2, textAlign: 'center' }}>
        <Chip
          label={`Level ${streak?.level || 1}: ${streak?.level_name || 'Getting Started'}`}
          color="primary"
          size="small"
        />
      </Box>
    </Paper>
  );
};

export default StreakWidget;