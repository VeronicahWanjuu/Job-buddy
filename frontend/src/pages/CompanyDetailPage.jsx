import { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  Button,
  Grid,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemText,
  Chip,
} from '@mui/material';
import {
  ArrowBack,
  Add,
  Business,
  Language,
  LocationOn,
} from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import api from '../services/api';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ContactCard from '../components/contacts/ContactCard';
import AddContactModal from '../components/contacts/AddContactModal';
import { formatDate } from '../utils/helpers';
import { STATUS_COLORS } from '../utils/constants';

const CompanyDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);
  const [tabValue, setTabValue] = useState(0);
  const [contactModalOpen, setContactModalOpen] = useState(false);
  const [editContact, setEditContact] = useState(null);

  useEffect(() => {
    fetchCompanyDetails();
  }, [id]);

  const fetchCompanyDetails = async () => {
    setLoading(true);
    try {
      const response = await api.get(`/companies/${id}`);
      setData(response.data);
    } catch (error) {
      toast.error('Failed to load company details');
      navigate('/companies');
    } finally {
      setLoading(false);
    }
  };

  const handleEditContact = (contact) => {
    setEditContact(contact);
    setContactModalOpen(true);
  };

  const handleDeleteContact = async (contact) => {
    if (!window.confirm(`Delete contact ${contact.name}?`)) return;

    try {
      await api.delete(`/contacts/${contact.id}`);
      toast.success('Contact deleted');
      fetchCompanyDetails();
    } catch (error) {
      toast.error('Failed to delete contact');
    }
  };

  const handleModalClose = () => {
    setContactModalOpen(false);
    setEditContact(null);
  };

  if (loading) {
    return <LoadingSpinner message="Loading company details..." />;
  }

  if (!data) {
    return null;
  }

  return (
    <Container maxWidth="lg">
      <Button
        startIcon={<ArrowBack />}
        onClick={() => navigate('/companies')}
        sx={{ mb: 2 }}
      >
        Back to Companies
      </Button>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'start', mb: 2 }}>
          <Business sx={{ fontSize: 48, color: 'primary.main', mr: 2 }} />
          <Box sx={{ flex: 1 }}>
            <Typography variant="h4" gutterBottom>
              {data.company.name}
            </Typography>
            
            {data.company.industry && (
              <Chip label={data.company.industry} sx={{ mb: 1 }} />
            )}

            {data.company.location && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <LocationOn fontSize="small" color="action" />
                <Typography variant="body2" color="text.secondary">
                  {data.company.location}
                </Typography>
              </Box>
            )}

            {data.company.website && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Language fontSize="small" color="action" />
                <Typography
                  variant="body2"
                  component="a"
                  href={data.company.website}
                  target="_blank"
                  rel="noopener noreferrer"
                  sx={{ color: 'primary.main', textDecoration: 'none' }}
                >
                  {data.company.website}
                </Typography>
              </Box>
            )}
          </Box>
        </Box>

        {data.company.notes && (
          <Box sx={{ mt: 2, p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
            <Typography variant="subtitle2" gutterBottom>
              Notes:
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {data.company.notes}
            </Typography>
          </Box>
        )}
      </Paper>

      <Paper sx={{ mb: 3 }}>
        <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)}>
          <Tab label={`Applications (${data.applications?.length || 0})`} />
          <Tab label={`Contacts (${data.contacts?.length || 0})`} />
        </Tabs>

        <Box sx={{ p: 3 }}>
          {tabValue === 0 && (
            <>
              {data.applications?.length > 0 ? (
                <List>
                  {data.applications.map((app) => (
                    <ListItem key={app.id} divider>
                      <ListItemText
                        primary={app.job_title}
                        secondary={`Applied: ${formatDate(app.applied_date || app.created_at)}`}
                      />
                      <Chip
                        label={app.status}
                        size="small"
                        sx={{
                          bgcolor: STATUS_COLORS[app.status],
                          color: 'white',
                        }}
                      />
                    </ListItem>
                  ))}
                </List>
              ) : (
                <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 3 }}>
                  No applications yet
                </Typography>
              )}
            </>
          )}

          {tabValue === 1 && (
            <>
              <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
                <Button
                  variant="contained"
                  startIcon={<Add />}
                  onClick={() => setContactModalOpen(true)}
                  size="small"
                >
                  Add Contact
                </Button>
              </Box>

              {data.contacts?.length > 0 ? (
                <Grid container spacing={2}>
                  {data.contacts.map((contact) => (
                    <Grid item xs={12} sm={6} key={contact.id}>
                      <ContactCard
                        contact={contact}
                        onEdit={handleEditContact}
                        onDelete={handleDeleteContact}
                      />
                    </Grid>
                  ))}
                </Grid>
              ) : (
                <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 3 }}>
                  No contacts yet
                </Typography>
              )}
            </>
          )}
        </Box>
      </Paper>

      <AddContactModal
        open={contactModalOpen}
        onClose={handleModalClose}
        onSuccess={fetchCompanyDetails}
        companyId={parseInt(id)}
        editContact={editContact}
      />
    </Container>
  );
};

export default CompanyDetailPage;