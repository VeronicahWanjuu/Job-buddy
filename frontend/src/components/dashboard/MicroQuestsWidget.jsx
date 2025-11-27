import { useState, useEffect, useCallback } from 'react';
import {
  Paper,
  Typography,
  Box,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Chip,
  ListItemIcon,
} from '@mui/material';
import { CheckCircle, Refresh, CheckCircleOutline } from '@mui/icons-material';
import api from '../../services/api';
import { toast } from 'react-toastify';

const MicroQuestsWidget = () => {
  const [quests, setQuests] = useState([]);

  const fetchQuests = useCallback(async () => {
    try {
      const response = await api.get('/goals/micro-quests');
      setQuests(response.data);
    } catch {
      toast.error('Failed to load micro-quests');
    }
  }, []);

  useEffect(() => {
    fetchQuests();
  }, [fetchQuests]);

  const handleComplete = async (questId) => {
    try {
      const response = await api.post(`/goals/micro-quests/${questId}/complete`);
      toast.success(`+${response.data.points_earned} points! 🎉`);
      fetchQuests(); // Refresh quests
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to complete quest');
    }
  };

  return (
    <Paper sx={{ p: 2.5, height: '100%', display: 'flex', flexDirection: 'column', flex: 1 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6" sx={{ fontWeight: 600 }}>Micro-Quests</Typography>
        <IconButton size="small" onClick={fetchQuests} color="primary">
          <Refresh />
        </IconButton>
      </Box>

      {quests.length === 0 ? (
        <Box sx={{ flexGrow: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Typography variant="body1" color="text.secondary" sx={{ textAlign: 'center' }}>
            🎉 All quests completed! Check back later for more.
          </Typography>
        </Box>
      ) : (
        <List sx={{ flexGrow: 1, overflow: 'auto', pr: 1 }}>
          {quests.map((quest) => (
            <ListItem key={quest.id} divider sx={{ py: 0.5 }}>
              <ListItemIcon sx={{ minWidth: 36 }}>
                <CheckCircleOutline color="primary" fontSize="small" />
              </ListItemIcon>
              <ListItemText
                primary={quest.title}
                secondary={
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      {quest.description}
                    </Typography>
                    <Chip
                      label={`${quest.points} points`}
                      size="small"
                      color="primary"
                      sx={{ mt: 0.5 }}
                    />
                  </Box>
                }
              />
              <ListItemSecondaryAction>
                <IconButton
                  edge="end"
                  onClick={() => handleComplete(quest.id)}
                  color="primary"
                >
                  <CheckCircle />
                </IconButton>
              </ListItemSecondaryAction>
            </ListItem>
          ))}
        </List>
      )}
    </Paper>
  );
};

export default MicroQuestsWidget;