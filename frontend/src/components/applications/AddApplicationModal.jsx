import { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  MenuItem,
  Box,
} from '@mui/material';
import { toast } from 'react-toastify';
import api from '../../services/api';
import { VALID_STATUSES } from '../../utils/constants';

const AddApplicationModal = ({ open, onClose, onSuccess }) => {
  const [companies, setCompanies] = useState([]);
  const [formData, setFormData] = useState({
    company_id: '',
    job_title: '',
    job_url: '',
    status: 'Planned',
    notes: '',
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (open) {
      fetchCompanies();
    }
  }, [open]);

  const fetchCompanies = async () => {
    try {
      const response = await api.get('/companies');
      setCompanies(response.data);
    } catch (err) {
      toast.error('Failed to load companies');
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: '' }));
    }
  };

  const validate = () => {
    const newErrors = {};

    if (!formData.company_id) {
      newErrors.company_id = 'Company is required';
    }
    if (!formData.job_title || formData.job_title.trim().length < 2) {
      newErrors.job_title = 'Job title is required';
    }
    if (!formData.status) {
      newErrors.status = 'Status is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async () => {
    if (!validate()) return;

    setLoading(true);
    try {
      await api.post('/applications', formData);
      toast.success('Application added successfully!');
      onSuccess();
      handleClose();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to add application');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setFormData({
      company_id: '',
      job_title: '',
      job_url: '',
      status: 'Planned',
      notes: '',
    });
    setErrors({});
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>Add New Application</DialogTitle>
      <DialogContent>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
          <TextField
            select
            fullWidth
            label="Company"
            name="company_id"
            value={formData.company_id}
            onChange={handleChange}
            error={!!errors.company_id}
            helperText={errors.company_id}
          >
            {companies.map((company) => (
              <MenuItem key={company.id} value={company.id}>
                {company.name}
              </MenuItem>
            ))}
          </TextField>

          <TextField
            fullWidth
            label="Job Title"
            name="job_title"
            value={formData.job_title}
            onChange={handleChange}
            error={!!errors.job_title}
            helperText={errors.job_title}
          />

          <TextField
            fullWidth
            label="Job URL (Optional)"
            name="job_url"
            value={formData.job_url}
            onChange={handleChange}
            placeholder="https://..."
          />

          <TextField
            select
            fullWidth
            label="Status"
            name="status"
            value={formData.status}
            onChange={handleChange}
            error={!!errors.status}
            helperText={errors.status}
          >
            {VALID_STATUSES.map((status) => (
              <MenuItem key={status} value={status}>
                {status}
              </MenuItem>
            ))}
          </TextField>

          <TextField
            fullWidth
            multiline
            rows={3}
            label="Notes (Optional)"
            name="notes"
            value={formData.notes}
            onChange={handleChange}
          />
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose}>Cancel</Button>
        <Button variant="contained" onClick={handleSubmit} disabled={loading}>
          {loading ? 'Adding...' : 'Add Application'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default AddApplicationModal;