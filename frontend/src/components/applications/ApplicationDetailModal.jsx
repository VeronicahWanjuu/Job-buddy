import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  Chip,
  Divider,
  List,
  ListItem,
  ListItemText,
  Tabs,
  Tab,
} from '@mui/material';
import {
  Business,
  CalendarToday,
  Link as LinkIcon,
  Description,
  Email,
} from '@mui/icons-material';
import { useState, useEffect } from 'react';
import { formatDate } from '../../utils/helpers';
import { STATUS_COLORS } from '../../utils/constants';
import api from '../../services/api';
import LoadingSpinner from '../common/LoadingSpinner';

const ApplicationDetailModal = ({ open, onClose, applicationId }) => {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);
  const [tabValue, setTabValue] = useState(0);

  useEffect(() => {
    if (open && applicationId) {
      fetchDetails();
    }
  }, [open, applicationId]);

  const fetchDetails = async () => {
    setLoading(true);
    try {
      const response = await api.get(`/applications/${applicationId}`);
      setData(response.data);
    } catch (error) {
      console.error('Failed to load application details', error);
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  if (!open) return null;

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        {data?.application.job_title || 'Application Details'}
      </DialogTitle>

      <DialogContent>
        {loading ? (
          <LoadingSpinner />
        ) : !data || !data.application ? (
          <Typography variant="body2" color="text.secondary" sx={{ py: 2, textAlign: 'center' }}>
            Failed to load application details
          </Typography>
        ) : (
          <>
            {/* Application Info */}
            <Box sx={{ mb: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <Business color="primary" />
                <Typography variant="h6">{data.application.company_name || 'Unknown Company'}</Typography>
              </Box>

              <Chip
                label={data.application.status || 'Unknown'}
                sx={{
                  bgcolor: STATUS_COLORS[data.application.status] || '#9E9E9E',
                  color: 'white',
                  mb: 2,
                }}
              />

              {data.application.applied_date && (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <CalendarToday fontSize="small" color="action" />
                  <Typography variant="body2" color="text.secondary">
                    Applied: {formatDate(data.application.applied_date)}
                  </Typography>
                </Box>
              )}

              {data.application.job_url && (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <LinkIcon fontSize="small" color="action" />
                  <Typography
                    variant="body2"
                    component="a"
                    href={data.application.job_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    sx={{ color: 'primary.main', textDecoration: 'none' }}
                  >
                    View Job Posting
                  </Typography>
                </Box>
              )}

              {data.application.notes && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Notes:
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {data.application.notes}
                  </Typography>
                </Box>
              )}
            </Box>

            <Divider sx={{ my: 2 }} />

            {/* Tabs for Outreach and CV Analyses */}
            <Tabs value={tabValue} onChange={handleTabChange}>
              <Tab label={`Outreach (${data.outreach?.length || 0})`} />
              <Tab label={`CV Analyses (${data.cv_analyses?.length || 0})`} />
            </Tabs>

            {/* Outreach Tab */}
            {tabValue === 0 && (
              <Box sx={{ mt: 2 }}>
                {data.outreach?.length > 0 ? (
                  <List>
                    {data.outreach.map((outreach) => (
                      <ListItem key={outreach.id} divider>
                        <ListItemText
                          primary={
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <Email fontSize="small" />
                              <Typography>{outreach.contact_name}</Typography>
                            </Box>
                          }
                          secondary={`${outreach.channel} • ${formatDate(outreach.sent_date)} • ${outreach.status}`}
                        />
                      </ListItem>
                    ))}
                  </List>
                ) : (
                  <Typography variant="body2" color="text.secondary" sx={{ py: 2, textAlign: 'center' }}>
                    No outreach activities yet
                  </Typography>
                )}
              </Box>
            )}

            {/* CV Analyses Tab */}
            {tabValue === 1 && (
              <Box sx={{ mt: 2 }}>
                {data.cv_analyses?.length > 0 ? (
                  <List>
                    {data.cv_analyses.map((analysis) => (
                      <ListItem key={analysis.id} divider>
                        <ListItemText
                          primary={
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <Description fontSize="small" />
                              <Typography>{analysis.cv_filename}</Typography>
                            </Box>
                          }
                          secondary={`ATS Score: ${analysis.ats_score}% • ${formatDate(analysis.created_at)}`}
                        />
                      </ListItem>
                    ))}
                  </List>
                ) : (
                  <Typography variant="body2" color="text.secondary" sx={{ py: 2, textAlign: 'center' }}>
                    No CV analyses yet
                  </Typography>
                )}
              </Box>
            )}
          </>
        )}
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
};

export default ApplicationDetailModal;