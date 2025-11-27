import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  IconButton,
  Menu,
  MenuItem,
} from '@mui/material';
import { MoreVert, Business, CalendarToday } from '@mui/icons-material';
import { useState } from 'react';
import { formatDate } from '../../utils/helpers';
import { STATUS_COLORS } from '../../utils/constants';

const ApplicationCard = ({ application, onView, onEdit, onDelete }) => {
  const [anchorEl, setAnchorEl] = useState(null);

  const getStatusColor = (status) => {
    const colors = {
      'Planned': '#757575',
      'Applied': '#2196F3',
      'Interview': '#FF9800',
      'Offer': '#4CAF50',
      'Rejected': '#F44336'
    };
    return colors[status] || '#757575';
  };

  const handleMenuOpen = (event) => {
    event.stopPropagation();
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleView = () => {
    handleMenuClose();
    onView(application);
  };

  const handleEdit = () => {
    handleMenuClose();
    onEdit(application);
  };

  const handleDelete = () => {
    handleMenuClose();
    onDelete(application);
  };

  return (
    <Card
      sx={{
        mb: 2,
        cursor: 'pointer',
        borderLeft: '4px solid',
        borderLeftColor: getStatusColor(application.status),
        '&:hover': {
          boxShadow: 3,
        },
      }}
      onClick={() => onView(application)}
    >
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
          <Box sx={{ flex: 1 }}>
            <Typography variant="h6" component="div" noWrap>
              {application.job_title}
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', mt: 1, gap: 0.5 }}>
              <Business sx={{ fontSize: 16, color: 'text.secondary' }} />
              <Typography variant="body2" color="text.secondary">
                {application.company_name}
              </Typography>
            </Box>
            {application.applied_date && (
              <Box sx={{ display: 'flex', alignItems: 'center', mt: 0.5, gap: 0.5 }}>
                <CalendarToday sx={{ fontSize: 16, color: 'text.secondary' }} />
                <Typography variant="caption" color="text.secondary">
                  Applied: {formatDate(application.applied_date)}
                </Typography>
              </Box>
            )}
          </Box>

          <IconButton
            size="small"
            onClick={handleMenuOpen}
            sx={{ ml: 1 }}
          >
            <MoreVert />
          </IconButton>
        </Box>

        {application.notes && (
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }} noWrap>
            {application.notes}
          </Typography>
        )}
      </CardContent>

      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={handleView}>View Details</MenuItem>
        <MenuItem onClick={handleEdit}>Edit</MenuItem>
        <MenuItem onClick={handleDelete} sx={{ color: 'error.main' }}>
          Delete
        </MenuItem>
      </Menu>
    </Card>
  );
};

export default ApplicationCard;