import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  Button,
  Avatar,
  Grid,
} from '@mui/material';
import { Email, LinkedIn } from '@mui/icons-material';
import { getInitials } from '../../utils/helpers';

const CoachCard = ({ coach }) => {
  return (
    <Card sx={{ maxWidth: 400, mx: 'auto', height: '100%', display: 'flex', flexDirection: 'column' }}>
      <CardContent sx={{ flexGrow: 1 }}>
        <Grid container spacing={2}>
          <Grid item xs={12} md={5}>
            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', mb: 2 }}>
              <Avatar
                sx={{ width: 60, height: 60, mb: 1, bgcolor: 'primary.main' }}
              >
                {getInitials(coach.name)}
              </Avatar>
              <Typography variant="h6" align="center">{coach.name}</Typography>
              <Typography variant="body2" color="text.secondary" align="center">
                {coach.title}
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} md={7}>
            <Chip
              label={coach.specialization}
              color="primary"
              size="small"
              sx={{ mb: 2 }}
            />

            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              {coach.bio}
            </Typography>

            <Box sx={{ mb: 1 }}>
              <Typography variant="body2">
                <strong>Rate:</strong> {coach.hourly_rate}/hour
              </Typography>
              <Typography variant="body2">
                <strong>Languages:</strong> {coach.languages.join(', ')}
              </Typography>
              <Chip
                label={coach.availability}
                size="small"
                color={coach.availability === 'Accepting new clients' ? 'success' : 'default'}
                sx={{ mt: 1 }}
              />
            </Box>
          </Grid>
        </Grid>
      </CardContent>

      <Box sx={{ p: 2, pt: 0, display: 'flex', gap: 1 }}>
        <Button
          size="small"
          variant="outlined"
          fullWidth
          startIcon={<Email />}
          href={`mailto:${coach.email}`}
        >
          EMAIL
        </Button>
        <Button
          size="small"
          variant="outlined"
          fullWidth
          startIcon={<LinkedIn />}
          href={coach.linkedin}
          target="_blank"
          rel="noopener noreferrer"
        >
          LINKEDIN
        </Button>
      </Box>
    </Card>
  );
};

export default CoachCard;