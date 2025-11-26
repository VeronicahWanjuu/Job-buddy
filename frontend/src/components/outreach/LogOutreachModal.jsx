import { useState } from 'react';
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
import { VALID_CHANNELS } from '../../utils/constants';

const LogOutreachModal = ({
  open,
  onClose,
  onSuccess,
  contactId,
  companyId,
  applicationId,
  prefilledData,
}) => {
  const [formData, setFormData] = useState({
    channel: 'email',
    message: prefilledData?.body || '',
    sent_date: new Date().toISOString().split('T')[0],
    follow_up_date: '',
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

    if (!formData.channel) {
      newErrors.channel = 'Channel is required';
    }
    if (!formData.message || formData.message.trim().length < 10) {
      newErrors.message = 'Message must be at least 10 characters';
    }
    if (!formData.sent_date) {
      newErrors.sent_date = 'Sent date is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async () => {
    if (!validate()) return;

    setLoading(true);
    try {
      const payload = {
        ...formData,
        contact_id: contactId,
        company_id: companyId,
        application_id: applicationId,
      };

      await api.post('/outreach', payload);
      toast.success('Outreach logged successfully!');
      onSuccess();
      handleClose();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to log outreach');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setFormData({
      channel: 'email',
      message: '',
      sent_date: new Date().toISOString().split('T')[0],
      follow_up_date: '',
    });
    setErrors({});
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>Log Outreach Activity</DialogTitle>
      <DialogContent>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
          <TextField
            select
            fullWidth
            label="Channel"
            name="channel"
            value={formData.channel}
            onChange={handleChange}
            error={!!errors.channel}
            helperText={errors.channel}
          >
            {VALID_CHANNELS.map((channel) => (
              <MenuItem key={channel} value={channel}>
                {channel.charAt(0).toUpperCase() + channel.slice(1)}
              </MenuItem>
            ))}
          </TextField>

          <TextField
            fullWidth
            multiline
            rows={6}
            label="Message"
            name="message"
            value={formData.message}
            onChange={handleChange}
            error={!!errors.message}
            helperText={errors.message}
          />

          <TextField
            fullWidth
            type="date"
            label="Sent Date"
            name="sent_date"
            value={formData.sent_date}
            onChange={handleChange}
            error={!!errors.sent_date}
            helperText={errors.sent_date}
            InputLabelProps={{ shrink: true }}
          />

          <TextField
            fullWidth
            type="date"
            label="Follow-up Date (Optional)"
            name="follow_up_date"
            value={formData.follow_up_date}
            onChange={handleChange}
            InputLabelProps={{ shrink: true }}
          />
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose}>Cancel</Button>
        <Button variant="contained" onClick={handleSubmit} disabled={loading}>
          {loading ? 'Logging...' : 'Log Outreach'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default LogOutreachModal;