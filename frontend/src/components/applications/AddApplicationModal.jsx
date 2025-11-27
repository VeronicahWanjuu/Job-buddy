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
  ToggleButtonGroup,
  ToggleButton,
} from '@mui/material';
import { Add, Business } from '@mui/icons-material';
import { toast } from 'react-toastify';
import api from '../../services/api';
import { VALID_STATUSES } from '../../utils/constants';
import AddCompanyModal from '../companies/AddCompanyModal';

const AddApplicationModal = ({ open, onClose, onSuccess }) => {
  const [companies, setCompanies] = useState([]);
  const [companyInputMode, setCompanyInputMode] = useState('select'); // 'select' or 'new'
  const [newCompanyName, setNewCompanyName] = useState('');
  const [addCompanyModalOpen, setAddCompanyModalOpen] = useState(false);
  const [formData, setFormData] = useState({
    company_id: '',
    company_name: '',
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
    } catch {
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

    if (companyInputMode === 'select') {
      if (!formData.company_id) {
        newErrors.company_id = 'Company is required';
      }
    } else {
      if (!newCompanyName || newCompanyName.trim().length < 2) {
        newErrors.company_name = 'Company name must be at least 2 characters';
      }
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
      let payload = { ...formData };
      
      if (companyInputMode === 'new' && newCompanyName) {
        try {
          const companyResponse = await api.post('/companies', {
            name: newCompanyName.trim(),
          });
          payload.company_id = companyResponse.data.id;
        } catch (companyError) {
          toast.error(companyError.response?.data?.error || 'Failed to create company');
          setLoading(false);
          return;
        }
      }
      
      delete payload.company_name;
      
      await api.post('/applications', payload);
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
      company_name: '',
      job_title: '',
      job_url: '',
      status: 'Planned',
      notes: '',
    });
    setNewCompanyName('');
    setCompanyInputMode('select');
    setErrors({});
    onClose();
  };

  const handleCompanyModalSuccess = () => {
    fetchCompanies();
    setAddCompanyModalOpen(false);
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>Add New Application</DialogTitle>
      <DialogContent>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
            <ToggleButtonGroup
              value={companyInputMode}
              exclusive
              onChange={(e, newMode) => {
                if (newMode) {
                  setCompanyInputMode(newMode);
                  setErrors((prev) => ({ ...prev, company_id: '', company_name: '' }));
                }
              }}
              size="small"
              fullWidth
            >
              <ToggleButton value="select">
                <Business sx={{ mr: 1, fontSize: 18 }} />
                Select Company
              </ToggleButton>
              <ToggleButton value="new">
                <Add sx={{ mr: 1, fontSize: 18 }} />
                New Company
              </ToggleButton>
            </ToggleButtonGroup>
          </Box>

          {companyInputMode === 'select' ? (
            <TextField
              select
              fullWidth
              label="Company"
              name="company_id"
              value={formData.company_id}
              onChange={handleChange}
              error={!!errors.company_id}
              helperText={errors.company_id || 'Select an existing company'}
            >
              {companies.length === 0 ? (
                <MenuItem disabled>No companies found. Create one first.</MenuItem>
              ) : (
                companies.map((company) => (
                  <MenuItem key={company.id} value={company.id}>
                    {company.name}
                  </MenuItem>
                ))
              )}
            </TextField>
          ) : (
            <TextField
              fullWidth
              label="Company Name"
              name="company_name"
              value={newCompanyName}
              onChange={(e) => setNewCompanyName(e.target.value)}
              error={!!errors.company_name}
              helperText={errors.company_name || 'Enter a new company name'}
              placeholder="e.g., Google, Microsoft"
            />
          )}

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

      <AddCompanyModal
        open={addCompanyModalOpen}
        onClose={() => setAddCompanyModalOpen(false)}
        onSuccess={handleCompanyModalSuccess}
      />
    </Dialog>
  );
};

export default AddApplicationModal;