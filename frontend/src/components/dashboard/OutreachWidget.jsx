import { Paper, Typography, Box, Button } from '@mui/material';
import { Send, Email } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

const OutreachWidget = ({ outreachGoal, outreachCurrent }) => {
  const navigate = useNavigate();
  const progress = outreachGoal ? (outreachCurrent / outreachGoal) * 100 : 0;

  const handleClick = () => {
    // Navigate to companies page where users can access contacts and generate outreach
    navigate('/companies');
  };

  return (
    <Paper
      sx={{
        p: 2,
        width: '100%',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: 90,
        background: 'linear-gradient(135deg, #ecfdf5 0%, #d1fae5 50%, #a7f3d0 100%)',
        borderLeft: '4px solid #10b981',
        cursor: 'pointer',
        transition: 'all 0.2s ease',
        '&:hover': {
          transform: 'translateY(-2px)',
          boxShadow: 4,
        },
      }}
      onClick={handleClick}
    >
      <Box sx={{ textAlign: 'center', width: '100%' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 1 }}>
          <Send sx={{ mr: 1, fontSize: 24, color: '#10b981' }} />
          <Typography variant="h6" sx={{ fontWeight: 600, color: '#047857' }}>
            Outreach
          </Typography>
        </Box>
        <Typography variant="body2" sx={{ color: '#065f46', fontWeight: 500, mb: 1 }}>
          {outreachCurrent || 0} / {outreachGoal || 0} this week
        </Typography>
        <Button
          variant="contained"
          size="small"
          startIcon={<Email />}
          onClick={(e) => {
            e.stopPropagation();
            handleClick();
          }}
          sx={{
            mt: 0.5,
            bgcolor: '#10b981',
            '&:hover': {
              bgcolor: '#059669',
            },
          }}
        >
          Generate Outreach
        </Button>
      </Box>
    </Paper>
  );
};

export default OutreachWidget;

