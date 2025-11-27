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
      setGroupedApplications(response.data.grouped_by_status);
    } catch {
      toast.error('Failed to load applications');
    } finally {
      setLoading(false);
    }
  };

      const handleDragEnd = async (result) => {
        const { destination, source, draggableId } = result;

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
      fetchApplications();
    } catch {
      toast.error('Failed to update application status');
      fetchApplications();
    }
  };

  const handleView = (application) => {
    setSelectedApplicationId(application.id);
    setDetailModalOpen(true);
  };

  const handleEdit = () => {
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
    } catch {
      toast.error('Failed to delete application');
    }
  };

  if (loading) {
    return <LoadingSpinner message="Loading applications..." />;
  }

  return (
    <Container maxWidth="xl" sx={{ py: 2, height: 'calc(100vh - 120px)', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', mb: 3, position: 'relative' }}>
        <Typography 
          variant="h4" 
          sx={{ 
            textAlign: 'center',
            textTransform: 'uppercase',
            fontWeight: 700,
            background: 'linear-gradient(135deg, #1e40af 0%, #06b6d4 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            letterSpacing: 2,
          }}
        >
          Applications
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setAddModalOpen(true)}
          sx={{ position: 'absolute', right: 0 }}
        >
          Add Application
        </Button>
      </Box>

      <Box sx={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
        <KanbanBoard
        groupedApplications={groupedApplications}
        onDragEnd={handleDragEnd}
        onView={handleView}
        onEdit={handleEdit}
        onDelete={handleDelete}
        onAddNew={() => setAddModalOpen(true)}
        />
      </Box>

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