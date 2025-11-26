import { useState } from 'react';
import {
  Box,
  Typography,
  TextField,
  Button,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Paper,
} from '@mui/material';
import { Add as AddIcon, Delete as DeleteIcon } from '@mui/icons-material';

const Step5Companies = ({ formData, setFormData }) => {
  const [companyName, setCompanyName] = useState('');
  const [companyWebsite, setCompanyWebsite] = useState('');

  // Ensure companies array exists
  const companies = formData.companies || [];

  const handleAddCompany = () => {
    if (companyName.trim()) {
      const newCompany = {
        name: companyName.trim(),
        website: companyWebsite.trim() || '',
      };
      setFormData({
        ...formData,
        companies: [...companies, newCompany],
      });
      setCompanyName('');
      setCompanyWebsite('');
    }
  };

  const handleRemoveCompany = (index) => {
    const newCompanies = companies.filter((_, i) => i !== index);
    setFormData({ ...formData, companies: newCompanies });
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAddCompany();
    }
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Add target companies (Optional)
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Add companies you're interested in. You can always add more later!
      </Typography>

      <Paper variant="outlined" sx={{ p: 2, mb: 2 }}>
        <TextField
          fullWidth
          label="Company Name"
          value={companyName}
          onChange={(e) => setCompanyName(e.target.value)}
          onKeyDown={handleKeyDown}
          sx={{ mb: 2 }}
        />

        <TextField
          fullWidth
          label="Website (Optional)"
          placeholder="https://example.com"
          value={companyWebsite}
          onChange={(e) => setCompanyWebsite(e.target.value)}
          onKeyDown={handleKeyDown}
          sx={{ mb: 2 }}
        />

        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleAddCompany}
          disabled={!companyName.trim()}
        >
          Add Company
        </Button>
      </Paper>

      {companies.length > 0 && (
        <Paper variant="outlined">
          <List>
            {companies.map((company, index) => (
              <ListItem
                key={index}
                divider={index < companies.length - 1}
              >
                <ListItemText
                  primary={company.name}
                  secondary={company.website || 'No website'}
                />

                <ListItemSecondaryAction>
                  <IconButton edge="end" onClick={() => handleRemoveCompany(index)}>
                    <DeleteIcon />
                  </IconButton>
                </ListItemSecondaryAction>
              </ListItem>
            ))}
          </List>
        </Paper>
      )}

      <Box sx={{ mt: 3, p: 2, bgcolor: 'info.light', borderRadius: 1 }}>
        <Typography variant="body2">
          💡 <strong>Tip:</strong> You've added{' '}
          {companies.length}{' '}
          compan{companies.length === 1 ? 'y' : 'ies'} so far.
        </Typography>
      </Box>
    </Box>
  );
};

export default Step5Companies;
