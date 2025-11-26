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
  MenuItem,
  Select,
  InputLabel,
  FormControl,
  Card,
  CardContent,
} from '@mui/material';
import { DragDropContext, Droppable, Draggable } from '@hello-pangea/dnd';
import { useForm, Controller } from 'react-hook-form';
import { toast } from 'react-toastify';
import api from '../api/axios';

const VALID_STATUSES = ['Planned', 'Applied', 'Interview', 'Offer', 'Rejected'];

const ApplicationColumn = ({ status, applications, onDragEnd }) => (
  <Droppable droppableId={status}>
    {(provided) => (
      <Box
        ref={provided.innerRef}
        {...provided.droppableProps}
        sx={{
          minWidth: 280,
          width: '20%',
          p: 1,
          m: 1,
          bgcolor: '#f4f5f7',
          borderRadius: 2,
          display: 'flex',
          flexDirection: 'column',
          maxHeight: '80vh',
          overflowY: 'auto',
        }}
      >
        <Typography variant="h6" sx={{ mb: 2, p: 1, bgcolor: '#e0e0e0', borderRadius: 1 }}>
          {status} ({applications.length})
        </Typography>
        {applications.map((app, index) => (
          <Draggable key={app.id} draggableId={String(app.id)} index={index}>
            {(provided) => (
              <Card
                ref={provided.innerRef}
                {...provided.draggableProps}
                {...provided.dragHandleProps}
                sx={{ mb: 1.5, boxShadow: 1, '&:hover': { boxShadow: 3 } }}
              >
                <CardContent>
                  <Typography variant="subtitle1" fontWeight="bold">
                    {app.job_title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {app.company_name}
                  </Typography>
                  <Typography variant="caption" color="text.disabled">
                    {app.applied_date ? `Applied: ${app.applied_date}` : 'Not applied yet'}
                  </Typography>
                </CardContent>
              </Card>
            )}
          </Draggable>
        ))}
        {provided.placeholder}
      </Box>
    )}
  </Droppable>
);

const Applications = () => {
  const [groupedApplications, setGroupedApplications] = useState({});
  const [companies, setCompanies] = useState([]);
  const [addModalOpen, setAddModalOpen] = useState(false);
  const [loading, setLoading] = useState(true);

  const {
    handleSubmit,
    control,
    reset,
    formState: { errors, isSubmitting },
  } = useForm({
    defaultValues: {
      company_id: '',
      job_title: '',
      job_url: '',
      status: 'Planned',
      notes: '',
    },
  });

  useEffect(() => {
    fetchApplicationsAndCompanies();
  }, []);

  const fetchApplicationsAndCompanies = async () => {
    try {
      setLoading(true);
      const [appsRes, companiesRes] = await Promise.all([
        api.get('/applications'),
        api.get('/companies'),
      ]);
      setGroupedApplications(appsRes.data.grouped_by_status);
      setCompanies(companiesRes.data);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to fetch data.');
    } finally {
      setLoading(false);
    }
  };

  const onDragEnd = async (result) => {
    const { source, destination, draggableId } = result;

    if (!destination) return;
    if (source.droppableId === destination.droppableId && source.index === destination.index) return;

    const sourceStatus = source.droppableId;
    const destinationStatus = destination.droppableId;
    const movedApplicationId = parseInt(draggableId, 10);

    const updatedGroupedApplications = { ...groupedApplications };
    const sourceApplications = [...updatedGroupedApplications[sourceStatus]];
    const [movedApp] = sourceApplications.splice(source.index, 1);

    movedApp.status = destinationStatus; // Update status in local data

    if (sourceStatus === destinationStatus) {
      sourceApplications.splice(destination.index, 0, movedApp);
      updatedGroupedApplications[sourceStatus] = sourceApplications;
    } else {
      const destinationApplications = [...updatedGroupedApplications[destinationStatus]];
      destinationApplications.splice(destination.index, 0, movedApp);
      updatedGroupedApplications[sourceStatus] = sourceApplications;
      updatedGroupedApplications[destinationStatus] = destinationApplications;
    }

    setGroupedApplications(updatedGroupedApplications); // Optimistic UI update

    try {
      await api.put(`/applications/${movedApplicationId}`, { status: destinationStatus });
      toast.success(`Application status updated to ${destinationStatus}!`);
      // Re-fetch to ensure data consistency and update goals/streaks
      fetchApplicationsAndCompanies();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to update application status.');
      // Revert UI on error (or just re-fetch)
      fetchApplicationsAndCompanies();
    }
  };

  const handleAddApplication = async (data) => {
    try {
      await api.post('/applications', data);
      toast.success('Application added successfully!');
      setAddModalOpen(false);
      reset();
      fetchApplicationsAndCompanies(); // Refresh data
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to add application.');
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
    <Container maxWidth="xl">
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
        <Typography variant="h4" component="h1">
          Applications Kanban Board
        </Typography>
        <Button variant="contained" onClick={() => setAddModalOpen(true)}>
          Add New Application
        </Button>
      </Box>

      <DragDropContext onDragEnd={onDragEnd}>
        <Box display="flex" overflow="auto">
          {VALID_STATUSES.map((status) => (
            <ApplicationColumn
              key={status}
              status={status}
              applications={groupedApplications[status] || []}
            />
          ))}
        </Box>
      </DragDropContext>

      {/* Add Application Modal */}
      <Dialog open={addModalOpen} onClose={() => setAddModalOpen(false)}>
        <DialogTitle>Add New Application</DialogTitle>
        <DialogContent>
          <form onSubmit={handleSubmit(handleAddApplication)}>
            <FormControl fullWidth margin="normal" error={!!errors.company_id}>
              <InputLabel id="company-label">Company</InputLabel>
              <Controller
                name="company_id"
                control={control}
                rules={{ required: 'Company is required' }}
                render={({ field }) => (
                  <Select
                    {...field}
                    labelId="company-label"
                    label="Company"
                    defaultValue=""
                  >
                    {companies.map((company) => (
                      <MenuItem key={company.id} value={company.id}>
                        {company.name}
                      </MenuItem>
                    ))}
                  </Select>
                )}
              />
              {errors.company_id && (
                <Typography color="error" variant="caption">
                  {errors.company_id.message}
                </Typography>
              )}
            </FormControl>

            <Controller
              name="job_title"
              control={control}
              rules={{ required: 'Job Title is required' }}
              render={({ field }) => (
                <TextField
                  {...field}
                  label="Job Title"
                  fullWidth
                  margin="normal"
                  error={!!errors.job_title}
                  helperText={errors.job_title?.message}
                />
              )}
            />
            <Controller
              name="job_url"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  label="Job URL"
                  fullWidth
                  margin="normal"
                  type="url"
                  error={!!errors.job_url}
                  helperText={errors.job_url?.message}
                />
              )}
            />
            <FormControl fullWidth margin="normal">
              <InputLabel id="status-label">Status</InputLabel>
              <Controller
                name="status"
                control={control}
                render={({ field }) => (
                  <Select
                    {...field}
                    labelId="status-label"
                    label="Status"
                  >
                    {VALID_STATUSES.map((status) => (
                      <MenuItem key={status} value={status}>
                        {status}
                      </MenuItem>
                    ))}
                  </Select>
                )}
              />
            </FormControl>
            <Controller
              name="notes"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  label="Notes"
                  fullWidth
                  multiline
                  rows={3}
                  margin="normal"
                />
              )}
            />
            <DialogActions>
              <Button onClick={() => setAddModalOpen(false)} disabled={isSubmitting}>
                Cancel
              </Button>
              <Button type="submit" variant="contained" disabled={isSubmitting}>
                {isSubmitting ? <CircularProgress size={24} /> : 'Add Application'}
              </Button>
            </DialogActions>
          </form>
        </DialogContent>
      </Dialog>
    </Container>
  );
};

export default Applications;