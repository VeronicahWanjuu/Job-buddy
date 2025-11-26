// frontend/src/pages/CoachesPage.jsx
import { useState, useEffect } from 'react';
import { Container, Typography, Grid } from '@mui/material';
import { toast } from 'react-toastify';
import api from '../services/api';
import LoadingSpinner from '../components/common/LoadingSpinner';
import CoachCard from '../components/coaches/CoachCard';

const CoachesPage = () => {
  const [loading, setLoading] = useState(true);
  const [coaches, setCoaches] = useState([]);

  useEffect(() => {
    fetchCoaches();
  }, []);

  const fetchCoaches = async () => {
    setLoading(true);
    try {
      const response = await api.get('/coaches');
      setCoaches(response.data);
    } catch (error) {
      toast.error('Failed to load coaches');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <LoadingSpinner message="Loading coaches..." />;
  }

  return (
    <Container maxWidth="lg">
      <Typography variant="h4" gutterBottom>
        Career Coaches
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Connect with professional career coaches to accelerate your job search
      </Typography>

      <Grid container spacing={3}>
        {coaches.map((coach) => (
          <Grid item xs={12} sm={6} md={4} key={coach.id}>
            <CoachCard coach={coach} />
          </Grid>
        ))}
      </Grid>
    </Container>
  );
};

export default CoachesPage;