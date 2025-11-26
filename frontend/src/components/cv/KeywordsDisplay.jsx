// frontend/src/components/cv/KeywordsDisplay.jsx
import { Box, Typography, Chip, Paper, Grid } from '@mui/material';
import { CheckCircle, Cancel } from '@mui/icons-material';

const KeywordsDisplay = ({ matched, missing }) => {
  return (
    <Grid container spacing={3} sx={{ mt: 2 }}>
      <Grid item xs={12} md={6}>
        <Paper sx={{ p: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <CheckCircle color="success" sx={{ mr: 1 }} />
            <Typography variant="h6">
              Matched Keywords ({matched.length})
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {matched.length > 0 ? (
              matched.map((keyword, index) => (
                <Chip
                  key={index}
                  label={keyword}
                  color="success"
                  size="small"
                />
              ))
            ) : (
              <Typography variant="body2" color="text.secondary">
                No matched keywords
              </Typography>
            )}
          </Box>
        </Paper>
      </Grid>

      <Grid item xs={12} md={6}>
        <Paper sx={{ p: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Cancel color="error" sx={{ mr: 1 }} />
            <Typography variant="h6">
              Missing Keywords ({missing.length})
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {missing.length > 0 ? (
              missing.map((keyword, index) => (
                <Chip
                  key={index}
                  label={keyword}
                  color="error"
                  size="small"
                  variant="outlined"
                />
              ))
            ) : (
              <Typography variant="body2" color="text.secondary">
                No missing keywords
              </Typography>
            )}
          </Box>
        </Paper>
      </Grid>
    </Grid>
  );
};

export default KeywordsDisplay;