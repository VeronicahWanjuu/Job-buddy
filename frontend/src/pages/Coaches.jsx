import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  CircularProgress,
  Grid,
  Card,
  CardContent,
  CardMedia,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Link,
} from '@mui/material';
import { toast } from 'react-toastify';
import api from '../api/axios';

const Coaches = () => {
  const [coaches, setCoaches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [tipOfTheDay, setTipOfTheDay] = useState(null);
  const [tipModalOpen, setTipModalOpen] = useState(false);

  useEffect(() => {
    fetchCoachesAndTip();
  }, []);

  const fetchCoachesAndTip = async () => {
    try {
      setLoading(true);
      const [coachesRes, tipRes] = await Promise.all([
        api.get('/coaches'),
        api.get('/coaches/tip-of-the-day'),
      ]);
      setCoaches(coachesRes.data);
      setTipOfTheDay(tipRes.data);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to fetch coaches or tip of the day.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="lg">
      <Typography variant="h4" component="h1" gutterBottom>
        Career Coaches
      </Typography>

      {tipOfTheDay && (
        <Card sx={{ mb: 4, bgcolor: 'info.light', color: 'info.contrastText' }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Tip of the Day from {tipOfTheDay.coach.name} ({tipOfTheDay.coach.specialization})
            </Typography>
            <Typography variant="body1">{tipOfTheDay.tip}</Typography>
            <Button variant="outlined" color="inherit" sx={{ mt: 2 }} onClick={() => setTipModalOpen(true)}>
              More About Coach
            </Button>
          </CardContent>
        </Card>
      )}

      <Grid container spacing={3}>
        {coaches.length > 0 ? (
          coaches.map((coach) => (
            <Grid item xs={12} sm={6} md={4} key={coach.id}>
              <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                <CardMedia
                  component="img"
                  height="140"
                  image={coach.image_url || 'https://via.placeholder.com/150'}
                  alt={coach.name}
                  sx={{ objectFit: 'cover' }}
                />
                <CardContent sx={{ flexGrow: 1 }}>
                  <Typography variant="h6" gutterBottom>
                    {coach.name}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {coach.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Specialization: {coach.specialization}
                  </Typography>
                  <Box sx={{ mt: 2 }}>
                    {coach.email && (
                      <Link href={`mailto:${coach.email}`} target="_blank" rel="noopener noreferrer" sx={{ mr: 1 }}>
                        Email
                      </Link>
                    )}
                    {coach.linkedin && (
                      <Link href={coach.linkedin} target="_blank" rel="noopener noreferrer">
                        LinkedIn
                      </Link>
                    )}
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))
        ) : (
          <Grid item xs={12}>
            <Typography>No coaches available at the moment.</Typography>
          </Grid>
        )}
      </Grid>

      {/* Tip of the Day Coach Detail Modal */}
      {tipOfTheDay && (
        <Dialog open={tipModalOpen} onClose={() => setTipModalOpen(false)}>
          <DialogTitle>About Coach {tipOfTheDay.coach.name}</DialogTitle>
          <DialogContent>
            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <CardMedia
                component="img"
                image={tipOfTheDay.coach.image_url || 'https://via.placeholder.com/150'}
                alt={tipOfTheDay.coach.name}
                sx={{ width: 100, height: 100, borderRadius: '50%', mb: 2, objectFit: 'cover' }}
              />
              <Typography variant="h6">{tipOfTheDay.coach.name}</Typography>
              <Typography variant="body1" color="text.secondary">{tipOfTheDay.coach.title}</Typography>
              <Typography variant="body2" color="text.secondary">Specialization: {tipOfTheDay.coach.specialization}</Typography>
              <Box sx={{ mt: 2 }}>
                {tipOfTheDay.coach.email && (
                  <Link href={`mailto:${tipOfTheDay.coach.email}`} target="_blank" rel="noopener noreferrer" sx={{ mr: 1 }}>
                    Email
                  </Link>
                )}
                {tipOfTheDay.coach.linkedin && (
                  <Link href={tipOfTheDay.coach.linkedin} target="_blank" rel="noopener noreferrer">
                    LinkedIn
                  </Link>
                )}
              </Box>
              <Typography variant="body2" sx={{mt: 2, fontStyle: 'italic'}}>""{tipOfTheDay.tip}""</Typography>
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setTipModalOpen(false)}>Close</Button>
          </DialogActions>
        </Dialog>
      )}
    </Container>
  );
};

export default Coaches;