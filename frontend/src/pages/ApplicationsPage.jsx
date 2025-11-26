import { useState, useEffect } from 'react';
import { Container, Typography, Box, Button } from '@mui/material';
import { Add } from '@mui/icons-material';
import { toast } from 'react-toastify';
import api from '../services/api';
import LoadingSpinner from '../components/common/LoadingSpinner';
import KanbanBoard from '../components/applications/KanbanBoard';
import AddApplicationModal from '../components/applications/AddApplicationModal';
import ApplicationDetailModal from '../components/applications/ApplicationDetailModal';
import { VALID_STATUSES } from '../utils/constants';

const ApplicationsPage = () => {
  const [loading, setLoading] = useState(true);
  const [applications, setApplications] = useState([]);
  const [groupedApplications, setGroupedApplications] = useState({});
  const [addModalOpen, setAddModalOpen] = useState(false);
  const [detailModalOpen, setDetailModalOpen] = useState(false);
  const [selectedApplicationId, setSelectedApplicationId] = useState(null);

  useEffect(() => {
    fetchApplications();
  }, []);

  const fetchApplications = async () => {
    setLoading(true);
    try {
      const response = await api.get('/applications');
      setApplications(response.data.applications);
      setGroupedApplications(response.data.grouped_by_status);
    } catch (error) {
      toast.error('Failed to load applications');
    } finally {
      setLoading(false);
    }
  };

  const handleDragEnd = async (result) => {
    const { destination, source, draggableId } = result;

    // Dropped outside the list
    if (!destination) return;

    // Dropped in same position
    if (
      destination.droppableId === source.droppableId &&
      destination.index === source.index
    ) {
      return;
    }

    const newStatus = destination.droppableId;
    const applicationId = parseInt(draggableId);

    // Optimistic update
    const newGrouped = { ...groupedApplications };
    const [movedApp] = newGrouped[source.droppableId].splice(source.index, 1);
    movedApp.status = newStatus;
    newGrouped[destination.droppableId].splice(destination.index, 0, movedApp);
    setGroupedApplications(newGrouped);

    // Backend update
    try {
      await api.put(`/applications/${applicationId}`, { status: newStatus });
      toast.success(`Application moved to ${newStatus}`);
      // Refresh to get updated data (including notifications, streak, goals)
      fetchApplications();
    } catch (error) {
      toast.error('Failed to update application status');
      // Revert on error
      fetchApplications();
    }
  };

  const handleView = (application) => {
    setSelectedApplicationId(application.id);
    setDetailModalOpen(true);
  };

  const handleEdit = (application) => {
    // TODO: Implement edit modal
    toast.info('Edit functionality coming soon');
  };

  const handleDelete = async (application) => {
    if (!window.confirm(`Delete application for ${application.job_title}?`)) {
      return;
    }

    try {
      await api.delete(`/applications/${application.id}`);
      toast.success('Application deleted');
      fetchApplications();
    } catch (error) {
      toast.error('Failed to delete application');
    }
  };

  if (loading) {
    return <LoadingSpinner message="Loading applications..." />;
  }

  return (
    <Container maxWidth="xl">
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Applications</Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setAddModalOpen(true)}
        >
          Add Application
        </Button>
      </Box>

      <KanbanBoard
        groupedApplications={groupedApplications}
        onDragEnd={handleDragEnd}
        onView={handleView}
        onEdit={handleEdit}
        onDelete={handleDelete}
        onAddNew={() => setAddModalOpen(true)}
      />

      <AddApplicationModal
        open={addModalOpen}
        onClose={() => setAddModalOpen(false)}
        onSuccess={fetchApplications}
      />

      <ApplicationDetailModal
        open={detailModalOpen}
        onClose={() => setDetailModalOpen(false)}
        applicationId={selectedApplicationId}
      />
    </Container>
  );
};

export default ApplicationsPage;