import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  Chip,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Grid,
} from '@mui/material';
import { toast } from 'react-toastify';
import api from '../api/axios';

const Resources = () => {
  const [resources, setResources] = useState([]);
  const [filteredResources, setFilteredResources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [categories, setCategories] = useState([]);
  const [types, setTypes] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedType, setSelectedType] = useState('');

  useEffect(() => {
    fetchResourcesAndFilters();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [resources, selectedCategory, selectedType]);

  const fetchResourcesAndFilters = async () => {
    try {
      setLoading(true);
      const [resourcesRes, filtersRes] = await Promise.all([
        api.get('/resources'),
        api.get('/resources/categories'),
      ]);
      setResources(resourcesRes.data);
      setCategories(filtersRes.data.categories);
      setTypes(filtersRes.data.types);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to fetch resources.');
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let tempResources = [...resources];

    if (selectedCategory) {
      tempResources = tempResources.filter((res) => res.category === selectedCategory);
    }
    if (selectedType) {
      tempResources = tempResources.filter((res) => res.type === selectedType);
    }
    setFilteredResources(tempResources);
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
        Learning Resources
      </Typography>

      <Box sx={{ display: 'flex', gap: 2, mb: 4 }}>
        <FormControl sx={{ minWidth: 150 }}>
          <InputLabel id="category-select-label">Category</InputLabel>
          <Select
            labelId="category-select-label"
            value={selectedCategory}
            label="Category"
            onChange={(e) => setSelectedCategory(e.target.value)}
          >
            <MenuItem value="">
              <em>All</em>
            </MenuItem>
            {categories.map((category) => (
              <MenuItem key={category} value={category}>
                {category}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        <FormControl sx={{ minWidth: 150 }}>
          <InputLabel id="type-select-label">Type</InputLabel>
          <Select
            labelId="type-select-label"
            value={selectedType}
            label="Type"
            onChange={(e) => setSelectedType(e.target.value)}
          >
            <MenuItem value="">
              <em>All</em>
            </MenuItem>
            {types.map((type) => (
              <MenuItem key={type} value={type}>
                {type}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Box>

      {filteredResources.length > 0 ? (
        <List>
          {filteredResources.map((resource) => (
            <ListItem
              key={resource.id}
              sx={{ borderBottom: 1, borderColor: 'divider', py: 2 }}
              alignItems="flex-start"
            >
              <ListItemText
                primary={
                  <Typography variant="h6" component="a" href={resource.url} target="_blank" rel="noopener noreferrer">
                    {resource.title}
                  </Typography>
                }
                secondary={
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      {resource.description}
                    </Typography>
                    <Box sx={{ mt: 1 }}>
                      {resource.category && (
                        <Chip label={resource.category} size="small" sx={{ mr: 1 }} />
                      )}
                      {resource.type && (
                        <Chip label={resource.type} size="small" sx={{ mr: 1 }} />
                      )}
                      {resource.difficulty && (
                        <Chip label={resource.difficulty} size="small" />
                      )}
                    </Box>
                  </Box>
                }
              />
            </ListItem>
          ))}
        </List>
      ) : (
        <Typography>No resources found matching your criteria.</Typography>
      )}
    </Container>
  );
};

export default Resources;