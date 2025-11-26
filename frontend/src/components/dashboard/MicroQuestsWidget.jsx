import { useState, useEffect } from 'react';
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
} from '@mui/material';
import { CheckCircle, Refresh } from '@mui/icons-material';
import api from '../../services/api';
import { toast } from 'react-toastify';

const MicroQuestsWidget = () => {
  const [quests, setQuests] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchQuests();
  }, []);

  const fetchQuests = async () => {
    try {
      const response = await api.get('/goals/micro-quests');
      setQuests(response.data);
    } catch (error) {
      toast.error('Failed to load micro-quests');
    } finally {
      setLoading(false);
    }
  };

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
    <Paper sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">Micro-Quests</Typography>
        <IconButton size="small" onClick={fetchQuests}>
          <Refresh />
        </IconButton>
      </Box>

      {quests.length === 0 ? (
        <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 3 }}>
          🎉 All quests completed! Check back later for more.
        </Typography>
      ) : (
        <List>
          {quests.map((quest) => (
            <ListItem key={quest.id} divider>
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