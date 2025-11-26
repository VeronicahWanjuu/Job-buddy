import { Box, Typography, Slider } from '@mui/material';

const Step4Goals = ({ formData, setFormData }) => {
  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Set your weekly goals
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 4 }}>
        These help keep you accountable. You can adjust them anytime!
      </Typography>

      <Box sx={{ mb: 4 }}>
        <Typography gutterBottom>
          Applications per week: <strong>{formData.weekly_application_goal}</strong>
        </Typography>
        <Slider
          value={formData.weekly_application_goal}
          onChange={(e, value) =>
            setFormData({ ...formData, weekly_application_goal: value })
          }
          min={1}
          max={20}
          marks={[
            { value: 1, label: '1' },
            { value: 5, label: '5' },
            { value: 10, label: '10' },
            { value: 15, label: '15' },
            { value: 20, label: '20' },
          ]}
          valueLabelDisplay="auto"
        />
      </Box>

      <Box>
        <Typography gutterBottom>
          Outreach activities per week: <strong>{formData.weekly_outreach_goal}</strong>
        </Typography>
        <Slider
          value={formData.weekly_outreach_goal}
          onChange={(e, value) =>
            setFormData({ ...formData, weekly_outreach_goal: value })
          }
          min={1}
          max={15}
          marks={[
            { value: 1, label: '1' },
            { value: 3, label: '3' },
            { value: 5, label: '5' },
            { value: 10, label: '10' },
            { value: 15, label: '15' },
          ]}
          valueLabelDisplay="auto"
        />
      </Box>

      <Box sx={{ mt: 3, p: 2, bgcolor: 'success.light', borderRadius: 1 }}>
        <Typography variant="body2">
          🎯 <strong>Recommended:</strong> Start with 5 applications and 3 outreach
          activities per week
        </Typography>
      </Box>
    </Box>
  );
};

export default Step4Goals;