import { Paper, Typography, Box, Chip } from '@mui/material';
import { Whatshot, EmojiEvents, Star, LocalFireDepartment } from '@mui/icons-material';

const StreakWidget = ({ streak }) => {
  return (
    <Paper sx={{ p: 2, height: '100%', width: '100%', display: 'flex', flexDirection: 'column', minHeight: 90 }}>
      <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
        Your Streak
      </Typography>

      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3, flexGrow: 1, justifyContent: 'center' }}>
        <LocalFireDepartment sx={{ fontSize: 50, color: 'error.main' }} />
        <Box>
          <Typography variant="h3">{streak?.current_streak || 0}</Typography>
          <Typography variant="body1" color="text.secondary">
            Day Streak
          </Typography>
        </Box>
      </Box>

      <Box sx={{ display: 'flex', justifyContent: 'space-around', mt: 'auto' }}>
        <Box sx={{ textAlign: 'center' }}>
          <EmojiEvents sx={{ color: 'gold', mb: 0.5, fontSize: 28 }} />
          <Typography variant="body2" color="text.secondary">
            Best Streak
          </Typography>
          <Typography variant="h6">{streak?.longest_streak || 0}</Typography>
        </Box>

        <Box sx={{ textAlign: 'center' }}>
          <Star sx={{ color: 'primary.main', mb: 0.5, fontSize: 28 }} />
          <Typography variant="body2" color="text.secondary">
            Level
          </Typography>
          <Typography variant="h6">{streak?.level || 1}</Typography>
        </Box>
      </Box>

      <Box sx={{ mt: 2, textAlign: 'center' }}>
        <Chip
          label={streak?.level_name || 'Getting Started'}
          color="primary"
          size="small"
        />
      </Box>
    </Paper>
  );
};

export default StreakWidget;