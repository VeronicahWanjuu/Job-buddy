import {
  Box,
  Typography,
  Card,
  CardActionArea,
  CardContent,
  Grid,
} from '@mui/material';
import {
  SentimentVerySatisfied,
  SentimentSatisfied,
  SentimentNeutral,
  SentimentDissatisfied,
} from '@mui/icons-material';
import { VALID_FEELINGS } from '../../utils/constants';

const feelingIcons = {
  'Excited and ready': <SentimentVerySatisfied sx={{ fontSize: 48 }} />,
  'Overwhelmed but motivated': <SentimentSatisfied sx={{ fontSize: 48 }} />,
  'Frustrated and stuck': <SentimentNeutral sx={{ fontSize: 48 }} />,
  'Just getting started': <SentimentDissatisfied sx={{ fontSize: 48 }} />,
};

const Step2Feeling = ({ formData, setFormData }) => {
  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        How are you feeling about your job search?
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        This helps us understand where you are in your journey
      </Typography>

      <Grid container spacing={2}>
        {VALID_FEELINGS.map((feeling) => (
          <Grid item xs={12} sm={6} key={feeling}>
            <Card
              sx={{
                border: formData.current_feeling === feeling ? '2px solid' : '1px solid',
                borderColor: formData.current_feeling === feeling ? 'primary.main' : 'divider',
                bgcolor: formData.current_feeling === feeling ? 'action.selected' : 'background.paper',
              }}
            >
              <CardActionArea
                onClick={() => setFormData({ ...formData, current_feeling: feeling })}
              >
                <CardContent sx={{ textAlign: 'center', py: 3 }}>
                  <Box sx={{ color: 'primary.main', mb: 1 }}>
                    {feelingIcons[feeling]}
                  </Box>
                  <Typography variant="body1" fontWeight="medium">
                    {feeling}
                  </Typography>
                </CardContent>
              </CardActionArea>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default Step2Feeling;