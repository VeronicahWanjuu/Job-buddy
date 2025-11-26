// frontend/src/components/cv/ATSScoreGauge.jsx
import { Box, Typography, CircularProgress } from '@mui/material';

const ATSScoreGauge = ({ score }) => {
  const getColor = (score) => {
    if (score >= 70) return '#4caf50'; // Green
    if (score >= 50) return '#ff9800'; // Orange
    return '#f44336'; // Red
  };

  const getLabel = (score) => {
    if (score >= 70) return 'Great Match!';
    if (score >= 50) return 'Good Match';
    return 'Needs Improvement';
  };

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        my: 4,
      }}
    >
      <Box sx={{ position: 'relative', display: 'inline-flex' }}>
        <CircularProgress
          variant="determinate"
          value={score}
          size={200}
          thickness={5}
          sx={{ color: getColor(score) }}
        />
        <Box
          sx={{
            top: 0,
            left: 0,
            bottom: 0,
            right: 0,
            position: 'absolute',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexDirection: 'column',
          }}
        >
          <Typography variant="h3" component="div" sx={{ fontWeight: 'bold' }}>
            {score}%
          </Typography>
          <Typography variant="body2" color="text.secondary">
            ATS Score
          </Typography>
        </Box>
      </Box>
      <Typography variant="h6" sx={{ mt: 2, color: getColor(score) }}>
        {getLabel(score)}
      </Typography>
    </Box>
  );
};

export default ATSScoreGauge;