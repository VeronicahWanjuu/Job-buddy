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
import { validateEmail } from '../../utils/validators';

const AddContactModal = ({ open, onClose, onSuccess, companyId, editContact }) => {
  const [formData, setFormData] = useState({
    name: editContact?.name || '',
    role: editContact?.role || '',
    email: editContact?.email || '',
    linkedin_url: editContact?.linkedin_url || '',
    notes: editContact?.notes || '',
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
      newErrors.name = 'Name must be at least 2 characters';
    }

    if (formData.email && !validateEmail(formData.email)) {
      newErrors.email = 'Invalid email format';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async () => {
    if (!validate()) return;

    setLoading(true);
    try {
      const payload = { ...formData, company_id: companyId };
      
      if (editContact) {
        await api.put(`/contacts/${editContact.id}`, formData);
        toast.success('Contact updated successfully!');
      } else {
        await api.post('/contacts', payload);
        toast.success('Contact added successfully!');
      }
      onSuccess();
      handleClose();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to save contact');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setFormData({
      name: '',
      role: '',
      email: '',
      linkedin_url: '',
      notes: '',
    });
    setErrors({});
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>{editContact ? 'Edit Contact' : 'Add New Contact'}</DialogTitle>
      <DialogContent>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
          <TextField
            fullWidth
            label="Name"
            name="name"
            value={formData.name}
            onChange={handleChange}
            error={!!errors.name}
            helperText={errors.name}
            required
          />

          <TextField
            fullWidth
            label="Role"
            name="role"
            value={formData.role}
            onChange={handleChange}
            placeholder="e.g., Recruiter, Hiring Manager"
          />

          <TextField
            fullWidth
            label="Email"
            name="email"
            type="email"
            value={formData.email}
            onChange={handleChange}
            error={!!errors.email}
            helperText={errors.email}
          />

          <TextField
            fullWidth
            label="LinkedIn URL"
            name="linkedin_url"
            value={formData.linkedin_url}
            onChange={handleChange}
            placeholder="https://linkedin.com/in/..."
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
          {loading ? 'Saving...' : editContact ? 'Update' : 'Add Contact'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default AddContactModal;