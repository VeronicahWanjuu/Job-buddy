import { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  List,
  ListItem,
  ListItemText,
  Chip,
  IconButton,
} from '@mui/material';
import { Visibility, Description } from '@mui/icons-material';
import { toast } from 'react-toastify';
import api from '../../services/api';
import LoadingSpinner from '../common/LoadingSpinner';
import EmptyState from '../common/EmptyState';
import { formatDateTime } from '../../utils/helpers';

const CVHistoryTab = ({ onViewAnalysis }) => {
  const [loading, setLoading] = useState(true);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const response = await api.get('/cv/history');
      setHistory(response.data);
    } catch {
      toast.error('Failed to load history');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <LoadingSpinner message="Loading history..." />;
  }

  if (history.length === 0) {
    return (
      <EmptyState
        icon={Description}
        title="No CV analyses yet"
        message="Analyze your first CV to see results here"
      />
    );
  }

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Analysis History
      </Typography>
      <List>
        {history.map((item) => (
          <Paper key={item.id} sx={{ mb: 2 }}>
            <ListItem
              secondaryAction={
                <IconButton
                  edge="end"
                  onClick={() => onViewAnalysis(item.id)}
                >
                  <Visibility />
                </IconButton>
              }
            >
              <ListItemText
                primary={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Description fontSize="small" />
                    <Typography>{item.cv_filename}</Typography>
                  </Box>
                }
                secondary={
                  <Box sx={{ mt: 1 }}>
                    <Chip
                      label={`ATS Score: ${item.ats_score}%`}
                      size="small"
                      color={item.ats_score >= 70 ? 'success' : item.ats_score >= 50 ? 'warning' : 'error'}
                      sx={{ mr: 1 }}
                    />
                    <Typography variant="caption" color="text.secondary">
                      {formatDateTime(item.created_at)}
                    </Typography>
                  </Box>
                }
              />
            </ListItem>
          </Paper>
        ))}
      </List>
    </Box>
  );
};

export default CVHistoryTab;