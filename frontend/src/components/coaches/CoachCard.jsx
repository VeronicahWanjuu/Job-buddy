// frontend/src/components/coaches/CoachCard.jsx
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  Button,
  Avatar,
} from '@mui/material';
import { Email, LinkedIn } from '@mui/icons-material';
import { getInitials } from '../../utils/helpers';

const CoachCard = ({ coach }) => {
  return (
    <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <CardContent sx={{ flexGrow: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'start', mb: 2 }}>
          <Avatar
            sx={{ width: 60, height: 60, mr: 2, bgcolor: 'primary.main' }}
          >
            {getInitials(coach.name)}
          </Avatar>
          <Box>
            <Typography variant="h6">{coach.name}</Typography>
            <Typography variant="body2" color="text.secondary">
              {coach.title}
            </Typography>
          </Box>
        </Box>

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
      </CardContent>

      <Box sx={{ p: 2, pt: 0, display: 'flex', gap: 1 }}>
        <Button
          fullWidth
          variant="outlined"
          startIcon={<Email />}
          href={`mailto:${coach.email}`}
        >
          Email
        </Button>
        <Button
          fullWidth
          variant="outlined"
          startIcon={<LinkedIn />}
          href={coach.linkedin}
          target="_blank"
          rel="noopener noreferrer"
        >
          LinkedIn
        </Button>
      </Box>
    </Card>
  );
};

export default CoachCard;