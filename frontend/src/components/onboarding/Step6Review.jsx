import {
  Box,
  Typography,
  Paper,
  List,
  ListItem,
  ListItemText,
  Divider,
  Chip,
} from '@mui/material';

const Step6Review = ({ formData }) => {
  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Review your profile
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Let's make sure everything looks good before we get started!
      </Typography>

      <Paper variant="outlined" sx={{ p: 3 }}>
        <List>
          <ListItem>
            <ListItemText
              primary="Current Feeling"
              secondary={formData.current_feeling}
            />
          </ListItem>
          <Divider />

          <ListItem>
            <ListItemText
              primary="Dream Milestone"
              secondary={formData.dream_milestone}
            />
          </ListItem>
          <Divider />

          <ListItem>
            <ListItemText
              primary="Weekly Application Goal"
              secondary={`${formData.weekly_application_goal} applications per week`}
            />
          </ListItem>
          <Divider />

          <ListItem>
            <ListItemText
              primary="Weekly Outreach Goal"
              secondary={`${formData.weekly_outreach_goal} outreach activities per week`}
            />
          </ListItem>
          <Divider />

          <ListItem>
            <ListItemText
              primary="Target Companies"
              secondary={
                (formData.companies && formData.companies.length > 0)
                  ? `${formData.companies.length} companies added`
                  : 'None added yet'
              }
            />
          </ListItem>
        </List>

        {formData.companies && formData.companies.length > 0 && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Your Target Companies:
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {formData.companies.map((company, index) => (
                <Chip key={index} label={company.name} />
              ))}
            </Box>
          </Box>
        )}
      </Paper>

      <Box sx={{ mt: 3, p: 2, bgcolor: 'success.light', borderRadius: 1 }}>
        <Typography variant="body2">
          ✅ Everything looks good? Click <strong>Submit</strong> to complete your setup!
        </Typography>
      </Box>
    </Box>
  );
};

export default Step6Review;