import { Box, Typography, TextField } from '@mui/material';

const Step3Dream = ({ formData, setFormData, errors }) => {
  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        What's your dream milestone?
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Describe the job or career goal you're working towards. Be specific!
      </Typography>

      <TextField
        fullWidth
        multiline
        rows={4}
        label="My dream milestone"
        placeholder="e.g., Become a Senior Software Engineer at a FAANG company, Land a Product Manager role at a startup, Transition to Data Science..."
        value={formData.dream_milestone}
        onChange={(e) =>
          setFormData({ ...formData, dream_milestone: e.target.value })
        }
        error={!!errors.dream_milestone}
        helperText={
          errors.dream_milestone ||
          `${formData.dream_milestone.length} characters (minimum 10)`
        }
      />

      <Box sx={{ mt: 3, p: 2, bgcolor: 'info.light', borderRadius: 1 }}>
        <Typography variant="body2">
          💡 <strong>Tip:</strong> A clear goal helps us tailor resources and track your
          progress effectively!
        </Typography>
      </Box>
    </Box>
  );
};

export default Step3Dream;