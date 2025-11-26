import { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Box,
} from '@mui/material';
import { toast } from 'react-toastify';
import api from '../../services/api';

const AddCompanyModal = ({ open, onClose, onSuccess, editCompany }) => {
  const [formData, setFormData] = useState({
    name: editCompany?.name || '',
    website: editCompany?.website || '',
    location: editCompany?.location || '',
    industry: editCompany?.industry || '',
    notes: editCompany?.notes || '',
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: '' }));
    }
  };

  const validate = () => {
    const newErrors = {};

    if (!formData.name || formData.name.trim().length < 2) {
      newErrors.name = 'Company name must be at least 2 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async () => {
    if (!validate()) return;

    setLoading(true);
    try {
      if (editCompany) {
        await api.put(`/companies/${editCompany.id}`, formData);
        toast.success('Company updated successfully!');
      } else {
        await api.post('/companies', formData);
        toast.success('Company added successfully!');
      }
      onSuccess();
      handleClose();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to save company');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setFormData({
      name: '',
      website: '',
      location: '',
      industry: '',
      notes: '',
    });
    setErrors({});
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>{editCompany ? 'Edit Company' : 'Add New Company'}</DialogTitle>
      <DialogContent>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
          <TextField
            fullWidth
            label="Company Name"
            name="name"
            value={formData.name}
            onChange={handleChange}
            error={!!errors.name}
            helperText={errors.name}
            required
          />

          <TextField
            fullWidth
            label="Website"
            name="website"
            value={formData.website}
            onChange={handleChange}
            placeholder="https://example.com"
          />

          <TextField
            fullWidth
            label="Location"
            name="location"
            value={formData.location}
            onChange={handleChange}
            placeholder="City, Country"
          />

          <TextField
            fullWidth
            label="Industry"
            name="industry"
            value={formData.industry}
            onChange={handleChange}
            placeholder="e.g., Technology, Finance"
          />

          <TextField
            fullWidth
            multiline
            rows={3}
            label="Notes"
            name="notes"
            value={formData.notes}
            onChange={handleChange}
          />
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose}>Cancel</Button>
        <Button variant="contained" onClick={handleSubmit} disabled={loading}>
          {loading ? 'Saving...' : editCompany ? 'Update' : 'Add Company'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default AddCompanyModal;