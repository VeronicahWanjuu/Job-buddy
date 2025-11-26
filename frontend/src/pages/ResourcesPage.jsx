// frontend/src/pages/ResourcesPage.jsx
import { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Grid,
  TextField,
  MenuItem,
} from '@mui/material';
import { toast } from 'react-toastify';
import api from '../services/api';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ResourceCard from '../components/resources/ResourceCard';

const ResourcesPage = () => {
  const [loading, setLoading] = useState(true);
  const [resources, setResources] = useState([]);
  const [filteredResources, setFilteredResources] = useState([]);
  const [categoryFilter, setCategoryFilter] = useState('');

  useEffect(() => {
    fetchResources();
  }, []);

  useEffect(() => {
    if (categoryFilter) {
      setFilteredResources(
        resources.filter((r) => r.category === categoryFilter)
      );
    } else {
      setFilteredResources(resources);
    }
  }, [categoryFilter, resources]);

  const fetchResources = async () => {
    setLoading(true);
    try {
      const response = await api.get('/resources');
      setResources(response.data);
      setFilteredResources(response.data);
    } catch (err) {
      toast.error('Failed to load resources');
    } finally {
      setLoading(false);
    }
  };

  const categories = [...new Set(resources.map((r) => r.category))];

  if (loading) {
    return <LoadingSpinner message="Loading resources..." />;
  }

  return (
    <Container maxWidth="lg">
      <Typography variant="h4" gutterBottom>
        Resources
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Curated resources to help you succeed in your job search
      </Typography>

      {resources.length > 0 && (
        <Box sx={{ mb: 3 }}>
          <TextField
            select
            label="Filter by Category"
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            sx={{ minWidth: 200 }}
            size="small"
          >
            <MenuItem value="">All Categories</MenuItem>
            {categories.map((category) => (
              <MenuItem key={category} value={category}>
                {category.replace('_', ' ').toUpperCase()}
              </MenuItem>
            ))}
          </TextField>
        </Box>
      )}

      <Grid container spacing={3}>
        {filteredResources.map((resource) => (
          <Grid item xs={12} sm={6} md={4} key={resource.id}>
            <ResourceCard resource={resource} />
          </Grid>
        ))}
      </Grid>
    </Container>
  );
};

export default ResourcesPage;