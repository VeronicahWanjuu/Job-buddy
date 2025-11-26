import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Button,
  Box,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  IconButton,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Card,
  CardContent,
  Grid,
} from '@mui/material';
import EventNoteIcon from '@mui/icons-material/EventNote';
import CalendarTodayIcon from '@mui/icons-material/CalendarToday';
import { useForm, Controller } from 'react-hook-form';
import { toast } from 'react-toastify';
import api from '../api/axios';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';

const Companies = () => {
  const [companies, setCompanies] = useState([]);
  const [selectedCompany, setSelectedCompany] = useState(null);
  const [addCompanyModalOpen, setAddCompanyModalOpen] = useState(false);
  const [editCompanyModalOpen, setEditCompanyModalOpen] = useState(false);
  const [addContactModalOpen, setAddContactModalOpen] = useState(false);
  const [editContactModalOpen, setEditContactModalOpen] = useState(false);
  const [selectedContact, setSelectedContact] = useState(null);
  const [loading, setLoading] = useState(true);
  const [generateOutreachModalOpen, setGenerateOutreachModalOpen] = useState(false);
  const [generatedOutreach, setGeneratedOutreach] = useState(null);
  const [selectedContactForOutreach, setSelectedContactForOutreach] = useState(null);
  const [logOutreachModalOpen, setLogOutreachModalOpen] = useState(false);

  const {
    handleSubmit,
    control,
    reset,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm();

  useEffect(() => {
    fetchCompanies();
  }, []);

  const fetchCompanies = async () => {
    try {
      setLoading(true);
      const response = await api.get('/companies');
      setCompanies(response.data);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to fetch companies.');
    } finally {
      setLoading(false);
    }
  };

  const fetchCompanyDetails = async (companyId) => {
    try {
      setLoading(true);
      const response = await api.get(`/companies/${companyId}`);
      setSelectedCompany(response.data);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to fetch company details.');
      setSelectedCompany(null); // Go back to list if fetching details fails
    } finally {
      setLoading(false);
    }
  };

  const handleAddCompany = async (data) => {
    try {
      await api.post('/companies', data);
      toast.success('Company added successfully!');
      setAddCompanyModalOpen(false);
      reset();
      fetchCompanies();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to add company.');
    }
  };

  const handleEditCompany = async (data) => {
    try {
      await api.put(`/companies/${selectedCompany.company.id}`, data);
      toast.success('Company updated successfully!');
      setEditCompanyModalOpen(false);
      fetchCompanyDetails(selectedCompany.company.id); // Refresh details
      fetchCompanies(); // Refresh company list
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to update company.');
    }
  };

  const handleDeleteCompany = async (companyId) => {
    if (window.confirm('Are you sure you want to delete this company? All associated applications and contacts will also be deleted.')) {
      try {
        await api.delete(`/companies/${companyId}`);
        toast.success('Company deleted successfully!');
        setSelectedCompany(null); // Go back to list view
        fetchCompanies();
      } catch (error) {
        toast.error(error.response?.data?.error || 'Failed to delete company.');
      }
    }
  };

  const handleAddContact = async (data) => {
    try {
      await api.post('/contacts', { ...data, company_id: selectedCompany.company.id });
      toast.success('Contact added successfully!');
      setAddContactModalOpen(false);
      reset();
      fetchCompanyDetails(selectedCompany.company.id); // Refresh details to show new contact
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to add contact.');
    }
  };

  const handleEditContact = async (data) => {
    try {
      await api.put(`/contacts/${selectedContact.id}`, data);
      toast.success('Contact updated successfully!');
      setEditContactModalOpen(false);
      setSelectedContact(null);
      fetchCompanyDetails(selectedCompany.company.id); // Refresh details
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to update contact.');
    }
  };

  const handleDeleteContact = async (contactId) => {
    if (window.confirm('Are you sure you want to delete this contact?')) {
      try {
        await api.delete(`/contacts/${contactId}`);
        toast.success('Contact deleted successfully!');
        fetchCompanyDetails(selectedCompany.company.id); // Refresh details
      } catch (error) {
        toast.error(error.response?.data?.error || 'Failed to delete contact.');
      }
    }
  };

  const openEditCompanyModal = (company) => {
    setValue('name', company.name);
    setValue('website', company.website);
    setValue('location', company.location);
    setValue('industry', company.industry);
    setValue('notes', company.notes);
    setEditCompanyModalOpen(true);
  };

  const openEditContactModal = (contact) => {
    setSelectedContact(contact); // Set selected contact for potential use in outreach
    setValue('name', contact.name);
    setValue('role', contact.role);
    setValue('email', contact.email);
    setValue('linkedin_url', contact.linkedin_url);
    setValue('notes', contact.notes);
    setEditContactModalOpen(true);
  };

  const openGenerateOutreachModal = (contact) => {
    setSelectedContactForOutreach(contact);
    setGeneratedOutreach(null); // Clear previous generated outreach
    reset({
        template_type: 'cold_outreach', // Default template type
        subject: '',
        body: '',
        sent_date: new Date().toISOString().split('T')[0], // Default to today
        follow_up_date: '',
    });
    setGenerateOutreachModalOpen(true);
  };

  const handleGenerateOutreach = async (data) => {
    if (!selectedContactForOutreach || !selectedCompany) return;

    try {
      const response = await api.post('/outreach/templates/generate', {
        contact_id: selectedContactForOutreach.id,
        company_id: selectedCompany.company.id,
        template_type: data.template_type,
        // application_id is optional, not included for now
      });
      setGeneratedOutreach(response.data);
      setValue('subject', response.data.subject);
      setValue('body', response.data.body);
      toast.success('Outreach template generated!');
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to generate outreach template.');
    }
  };

  const handleLogOutreach = async (data) => {
    if (!selectedContactForOutreach || !selectedCompany) return;

    try {
      const submissionData = {
        contact_id: selectedContactForOutreach.id,
        company_id: selectedCompany.company.id,
        channel: 'email', // Assuming email for generated outreach
        message: data.body,
        sent_date: data.sent_date,
        follow_up_date: data.follow_up_date || null,
        // application_id is optional, not included for now
      };
      await api.post('/outreach', submissionData);
      toast.success('Outreach logged successfully!');
      setLogOutreachModalOpen(false);
      setGenerateOutreachModalOpen(false); // Close generation modal too
      fetchCompanyDetails(selectedCompany.company.id); // Refresh company details to show new outreach
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to log outreach.');
    }
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
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
        {selectedCompany ? (
          <Button startIcon={<ArrowBackIcon />} onClick={() => setSelectedCompany(null)}>
            Back to Companies
          </Button>
        ) : (
          <Typography variant="h4" component="h1">
            Companies
          </Typography>
        )}
        {!selectedCompany && (
          <Button variant="contained" startIcon={<AddIcon />} onClick={() => {
            reset();
            setAddCompanyModalOpen(true);
          }}>
            Add New Company
          </Button>
        )}
        {selectedCompany && (
            <Box>
                <Button variant="outlined" startIcon={<EditIcon />} sx={{mr: 1}} onClick={() => openEditCompanyModal(selectedCompany.company)}>
                    Edit Company
                </Button>
                <Button variant="outlined" color="error" startIcon={<DeleteIcon />} onClick={() => handleDeleteCompany(selectedCompany.company.id)}>
                    Delete Company
                </Button>
            </Box>
        )}
      </Box>

      {selectedCompany ? (
        // Company Detail View
        <Box>
          <Card sx={{ mb: 4 }}>
            <CardContent>
              <Typography variant="h5" gutterBottom>
                {selectedCompany.company.name}
              </Typography>
              <Typography variant="body1">Website: <a href={selectedCompany.company.website} target="_blank" rel="noopener noreferrer">{selectedCompany.company.website}</a></Typography>
              <Typography variant="body1">Location: {selectedCompany.company.location || 'N/A'}</Typography>
              <Typography variant="body1">Industry: {selectedCompany.company.industry || 'N/A'}</Typography>
              <Typography variant="body2" color="text.secondary">Notes: {selectedCompany.company.notes || 'No notes'}</Typography>
            </CardContent>
          </Card>

          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                    <Typography variant="h6">Contacts</Typography>
                    <Button variant="contained" size="small" startIcon={<AddIcon />} onClick={() => {
                        reset();
                        setAddContactModalOpen(true);
                    }}>
                      Add Contact
                    </Button>
                  </Box>
                  {selectedCompany.contacts && selectedCompany.contacts.length > 0 ? (
                    <List>
                      {selectedCompany.contacts.map((contact) => (
                        <ListItem
                          key={contact.id}
                          secondaryAction={
                            <Box>
                              <IconButton edge="end" aria-label="generate outreach" onClick={() => openGenerateOutreachModal(contact)}>
                                <EventNoteIcon />
                              </IconButton>
                              <IconButton edge="end" aria-label="edit" onClick={() => openEditContactModal(contact)}>
                                <EditIcon />
                              </IconButton>
                              <IconButton edge="end" aria-label="delete" onClick={() => handleDeleteContact(contact.id)}>
                                <DeleteIcon />
                              </IconButton>
                            </Box>
                          }
                        >
                          <ListItemText
                            primary={contact.name}
                            secondary={`${contact.role || 'N/A'} - ${contact.email || 'N/A'}`}
                          />
                        </ListItem>
                      ))}
                    </List>
                  ) : (
                    <Typography>No contacts for this company.</Typography>
                  )}
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Applications
                  </Typography>
                  {selectedCompany.applications && selectedCompany.applications.length > 0 ? (
                    <List>
                      {selectedCompany.applications.map((app) => (
                        <ListItem key={app.id}>
                          <ListItemText
                            primary={app.job_title}
                            secondary={`Status: ${app.status} - Applied: ${app.applied_date || 'N/A'}`}
                          />
                        </ListItem>
                      ))}
                    </List>
                  ) : (
                    <Typography>No applications for this company.</Typography>
                  )}
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Box>
      ) : (
        // Company List View
        <Grid container spacing={3}>
          {companies.length > 0 ? (
            companies.map((company) => (
              <Grid item xs={12} sm={6} md={4} key={company.id}>
                <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      {company.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {company.industry} - {company.location}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{mt: 1}}>
                      <a href={company.website} target="_blank" rel="noopener noreferrer">{company.website}</a>
                    </Typography>
                  </CardContent>
                  <CardActions>
                    <Button size="small" onClick={() => fetchCompanyDetails(company.id)}>
                      View Details
                    </Button>
                    <IconButton size="small" onClick={() => openEditCompanyModal(company)}>
                      <EditIcon />
                    </IconButton>
                    <IconButton size="small" color="error" onClick={() => handleDeleteCompany(company.id)}>
                      <DeleteIcon />
                    </IconButton>
                  </CardActions>
                </Card>
              </Grid>
            ))
          ) : (
            <Grid item xs={12}>
              <Typography>No companies added yet.</Typography>
            </Grid>
          )}
        </Grid>
      )}

      {/* Add Company Modal */}
      <Dialog open={addCompanyModalOpen} onClose={() => setAddCompanyModalOpen(false)}>
        <DialogTitle>Add New Company</DialogTitle>
        <DialogContent>
          <form>
            <Controller
              name="name"
              control={control}
              rules={{ required: 'Company name is required', minLength: { value: 2, message: 'Name must be at least 2 characters' } }}
              render={({ field }) => (
                <TextField {...field} label="Company Name" fullWidth margin="normal" error={!!errors.name} helperText={errors.name?.message} />
              )}
            />
            <Controller
              name="website"
              control={control}
              render={({ field }) => <TextField {...field} label="Website" fullWidth margin="normal" />}
            />
            <Controller
              name="location"
              control={control}
              render={({ field }) => <TextField {...field} label="Location" fullWidth margin="normal" />}
            />
            <Controller
              name="industry"
              control={control}
              render={({ field }) => <TextField {...field} label="Industry" fullWidth margin="normal" />}
            />
            <Controller
              name="notes"
              control={control}
              render={({ field }) => <TextField {...field} label="Notes" fullWidth multiline rows={3} margin="normal" />}
            />
          </form>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAddCompanyModalOpen(false)} disabled={isSubmitting}>Cancel</Button>
          <Button onClick={handleSubmit(handleAddCompany)} variant="contained" disabled={isSubmitting}>
            {isSubmitting ? <CircularProgress size={24} /> : 'Add Company'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Edit Company Modal */}
      <Dialog open={editCompanyModalOpen} onClose={() => setEditCompanyModalOpen(false)}>
        <DialogTitle>Edit Company</DialogTitle>
        <DialogContent>
          <form>
            <Controller
              name="name"
              control={control}
              rules={{ required: 'Company name is required', minLength: { value: 2, message: 'Name must be at least 2 characters' } }}
              render={({ field }) => (
                <TextField {...field} label="Company Name" fullWidth margin="normal" error={!!errors.name} helperText={errors.name?.message} />
              )}
            />
            <Controller
              name="website"
              control={control}
              render={({ field }) => <TextField {...field} label="Website" fullWidth margin="normal" />}
            />
            <Controller
              name="location"
              control={control}
              render={({ field }) => <TextField {...field} label="Location" fullWidth margin="normal" />}
            />
            <Controller
              name="industry"
              control={control}
              render={({ field }) => <TextField {...field} label="Industry" fullWidth margin="normal" />}
            />
            <Controller
              name="notes"
              control={control}
              render={({ field }) => <TextField {...field} label="Notes" fullWidth multiline rows={3} margin="normal" />}
            />
          </form>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditCompanyModalOpen(false)} disabled={isSubmitting}>Cancel</Button>
          <Button onClick={handleSubmit(handleEditCompany)} variant="contained" disabled={isSubmitting}>
            {isSubmitting ? <CircularProgress size={24} /> : 'Save Changes'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Add Contact Modal */}
      <Dialog open={addContactModalOpen} onClose={() => setAddContactModalOpen(false)}>
        <DialogTitle>Add New Contact for {selectedCompany?.company.name}</DialogTitle>
        <DialogContent>
          <form>
            <Controller
              name="name"
              control={control}
              rules={{ required: 'Contact name is required', minLength: { value: 2, message: 'Name must be at least 2 characters' } }}
              render={({ field }) => (
                <TextField {...field} label="Contact Name" fullWidth margin="normal" error={!!errors.name} helperText={errors.name?.message} />
              )}
            />
            <Controller
              name="role"
              control={control}
              render={({ field }) => <TextField {...field} label="Role" fullWidth margin="normal" />}
            />
            <Controller
              name="email"
              control={control}
              rules={{ pattern: { value: /^\S+@\S+$/i, message: 'Invalid email address' } }}
              render={({ field }) => <TextField {...field} label="Email" fullWidth margin="normal" error={!!errors.email} helperText={errors.email?.message} />}
            />
            <Controller
              name="linkedin_url"
              control={control}
              render={({ field }) => <TextField {...field} label="LinkedIn URL" fullWidth margin="normal" />}
            />
            <Controller
              name="notes"
              control={control}
              render={({ field }) => <TextField {...field} label="Notes" fullWidth multiline rows={3} margin="normal" />}
            />
          </form>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAddContactModalOpen(false)} disabled={isSubmitting}>Cancel</Button>
          <Button onClick={handleSubmit(handleAddContact)} variant="contained" disabled={isSubmitting}>
            {isSubmitting ? <CircularProgress size={24} /> : 'Add Contact'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Edit Contact Modal */}
      <Dialog open={editContactModalOpen} onClose={() => setEditContactModalOpen(false)}>
        <DialogTitle>Edit Contact for {selectedCompany?.company.name}</DialogTitle>
        <DialogContent>
          <form>
            <Controller
              name="name"
              control={control}
              rules={{ required: 'Contact name is required', minLength: { value: 2, message: 'Name must be at least 2 characters' } }}
              render={({ field }) => (
                <TextField {...field} label="Contact Name" fullWidth margin="normal" error={!!errors.name} helperText={errors.name?.message} />
              )}
            />
            <Controller
              name="role"
              control={control}
              render={({ field }) => <TextField {...field} label="Role" fullWidth margin="normal" />}
            />
            <Controller
              name="email"
              control={control}
              rules={{ pattern: { value: /^\S+@\S+$/i, message: 'Invalid email address' } }}
              render={({ field }) => <TextField {...field} label="Email" fullWidth margin="normal" error={!!errors.email} helperText={errors.email?.message} />}
            />
            <Controller
              name="linkedin_url"
              control={control}
              render={({ field }) => <TextField {...field} label="LinkedIn URL" fullWidth margin="normal" />}
            />
            <Controller
              name="notes"
              control={control}
              render={({ field }) => <TextField {...field} label="Notes" fullWidth multiline rows={3} margin="normal" />}
            />
          </form>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditContactModalOpen(false)} disabled={isSubmitting}>Cancel</Button>
          <Button onClick={handleSubmit(handleEditContact)} variant="contained" disabled={isSubmitting}>
            {isSubmitting ? <CircularProgress size={24} /> : 'Save Changes'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Generate Outreach Modal */}
      <Dialog open={generateOutreachModalOpen} onClose={() => setGenerateOutreachModalOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Generate Outreach for {selectedContactForOutreach?.name}</DialogTitle>
        <DialogContent>
          <Box component="form" onSubmit={handleSubmit(handleGenerateOutreach)}>
            <FormControl fullWidth margin="normal">
              <InputLabel id="template-type-label">Template Type</InputLabel>
              <Controller
                name="template_type"
                control={control}
                render={({ field }) => (
                  <Select {...field} labelId="template-type-label" label="Template Type">
                    <MenuItem value="cold_outreach">Cold Outreach</MenuItem>
                    {/* Add more template types as needed */}
                  </Select>
                )}
              />
            </FormControl>
            <Button
                variant="contained"
                onClick={handleSubmit(handleGenerateOutreach)}
                disabled={isSubmitting}
                sx={{ mt: 2, mb: 2 }}
            >
                {isSubmitting ? <CircularProgress size={24} /> : 'Generate Template'}
            </Button>
          </Box>

          {generatedOutreach && (
            <Box sx={{ mt: 3, p: 2, border: '1px solid #ccc', borderRadius: 1 }}>
              <Typography variant="h6" gutterBottom>Generated Content</Typography>
              <TextField
                label="Subject"
                fullWidth
                margin="normal"
                value={generatedOutreach.subject}
                onChange={(e) => setGeneratedOutreach(prev => ({...prev, subject: e.target.value}))}
              />
              <TextField
                label="Body"
                fullWidth
                multiline
                rows={10}
                margin="normal"
                value={generatedOutreach.body}
                onChange={(e) => setGeneratedOutreach(prev => ({...prev, body: e.target.value}))}
              />
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                Editing Tips: {generatedOutreach.editing_tips || 'None'}
              </Typography>
              
              <Box sx={{ display: 'flex', gap: 2, mt: 3 }}>
                <Controller
                    name="sent_date"
                    control={control}
                    render={({ field }) => (
                        <TextField
                            {...field}
                            label="Sent Date"
                            type="date"
                            fullWidth
                            InputLabelProps={{ shrink: true }}
                            error={!!errors.sent_date}
                            helperText={errors.sent_date?.message}
                        />
                    )}
                />
                <Controller
                    name="follow_up_date"
                    control={control}
                    render={({ field }) => (
                        <TextField
                            {...field}
                            label="Follow-up Date (Optional)"
                            type="date"
                            fullWidth
                            InputLabelProps={{ shrink: true }}
                            error={!!errors.follow_up_date}
                            helperText={errors.follow_up_date?.message}
                        />
                    )}
                />
              </Box>

              <Button
                variant="contained"
                onClick={handleSubmit(handleLogOutreach)}
                disabled={isSubmitting}
                sx={{ mt: 3 }}
                startIcon={isSubmitting ? <CircularProgress size={20} /> : <EventNoteIcon />}
              >
                Log This Outreach
              </Button>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setGenerateOutreachModalOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default Companies;