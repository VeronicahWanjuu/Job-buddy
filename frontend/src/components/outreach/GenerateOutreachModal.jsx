import { useState, useEffect, useCallback } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  MenuItem,
  Box,
  Alert,
  CircularProgress,
} from '@mui/material';
import { toast } from 'react-toastify';
import api from '../../services/api';

const TEMPLATE_TYPES = [
  { value: 'cold_outreach', label: 'Cold Outreach to Recruiter' },
  { value: 'follow_up_application', label: 'Follow-up After Application' },
  { value: 'networking_connection', label: 'LinkedIn Connection Request' },
  { value: 'thank_you_interview', label: 'Thank You After Interview' },
  { value: 'informational_interview', label: 'Request for Informational Interview' },
];

const GenerateOutreachModal = ({ open, onClose, contactId, companyId, applicationId }) => {
  const [loading, setLoading] = useState(false);
  const [templateType, setTemplateType] = useState('cold_outreach');
  const [subject, setSubject] = useState('');
  const [body, setBody] = useState('');
  const [editingTips, setEditingTips] = useState('');

  const generateTemplate = useCallback(async () => {
    setLoading(true);
    try {
      const response = await api.post('/outreach/templates/generate', {
        contact_id: contactId,
        company_id: companyId,
        application_id: applicationId,
        template_type: templateType,
      });

      setSubject(response.data.subject);
      setBody(response.data.body);
      setEditingTips(response.data.editing_tips);
    } catch {
      toast.error('Failed to generate template');
    } finally {
      setLoading(false);
    }
  }, [contactId, companyId, applicationId, templateType]);

  useEffect(() => {
    if (open && contactId && companyId) {
      generateTemplate();
    }
  }, [open, contactId, companyId, templateType, generateTemplate]);

  const handleLogOutreach = () => {
    onClose({ subject, body });
  };

  const handleClose = () => {
    setSubject('');
    setBody('');
    setEditingTips('');
    onClose(null);
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>Generate Outreach Message</DialogTitle>
      <DialogContent>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
          <TextField
            select
            fullWidth
            label="Template Type"
            value={templateType}
            onChange={(e) => setTemplateType(e.target.value)}
          >
            {TEMPLATE_TYPES.map((template) => (
              <MenuItem key={template.value} value={template.value}>
                {template.label}
              </MenuItem>
            ))}
          </TextField>

          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
              <CircularProgress />
            </Box>
          ) : (
            <>
              {editingTips && (
                <Alert severity="info" sx={{ whiteSpace: 'pre-line' }}>
                  {editingTips}
                </Alert>
              )}

              <TextField
                fullWidth
                label="Subject"
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
              />

              <TextField
                fullWidth
                multiline
                rows={12}
                label="Message Body"
                value={body}
                onChange={(e) => setBody(e.target.value)}
              />
            </>
          )}
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose}>Cancel</Button>
        <Button variant="contained" onClick={handleLogOutreach} disabled={loading || !body}>
          Log This Outreach
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default GenerateOutreachModal;