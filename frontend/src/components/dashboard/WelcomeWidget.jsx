import { Paper, Typography, Box } from '@mui/material';
import { EmojiPeople } from '@mui/icons-material';

const WelcomeWidget = ({ userName, dreamMilestone }) => {
  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  return (
    <Paper 
      sx={{ 
        p: 2.5, 
        width: '100%',
        height: '100%',
        background: 'linear-gradient(135deg, #dbeafe 0%, #bfdbfe 50%, #93c5fd 100%)', 
        borderLeft: '5px solid #1e40af',
        minHeight: '120px',
        position: 'relative',
        overflow: 'hidden',
        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
      }}
    >
      <Box sx={{ position: 'relative', zIndex: 1, display: 'flex', alignItems: 'center', justifyContent: 'space-between', height: '100%' }}>
        <Box sx={{ flex: 1 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <EmojiPeople sx={{ mr: 1.5, fontSize: 28, color: '#1e40af' }} />
            <Typography variant="h6" color="#1e40af" sx={{ fontWeight: 700 }}>
              {getGreeting()}, {userName}!
            </Typography>
          </Box>
          <Typography variant="body1" sx={{ color: '#1e3a8a', fontWeight: 600, mb: 0.5 }}>
            Your goal: <strong style={{ color: '#1e40af' }}>{dreamMilestone}</strong>
          </Typography>
          <Typography variant="body2" sx={{ mt: 0.5, color: '#3b82f6', display: 'block', fontWeight: 500 }}>
            Let's make today count! 💪
          </Typography>
        </Box>
      </Box>
    </Paper>
  );
};

export default WelcomeWidget;