import React, { useState, useEffect, useContext } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  LinearProgress,
  Button,
  Box,
  List,
  ListItem,
  ListItemText,
  CircularProgress,
} from '@mui/material';
import { AuthContext } from '../contexts/AuthContext';
import api from '../api/axios';
import { toast } from 'react-toastify';
import { useNavigate } from 'react-router-dom';

const Dashboard = () => {
  const { user } = useContext(AuthContext);
  const navigate = useNavigate();
  const [onboardingData, setOnboardingData] = useState(null);
  const [goals, setGoals] = useState(null);
  const [streak, setStreak] = useState(null);
  const [microQuests, setMicroQuests] = useState([]);
  const [recentApplications, setRecentApplications] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch onboarding data
        const onboardingRes = await api.get('/onboarding');
        if (onboardingRes.data.completed) {
          setOnboardingData(onboardingRes.data);
        }

        // Fetch goals
        const goalsRes = await api.get('/goals/current');
        setGoals(goalsRes.data);

        // Fetch streak
        const streakRes = await api.get('/goals/streak');
        setStreak(streakRes.data);

        // Fetch micro-quests
        const questsRes = await api.get('/goals/micro-quests');
        setMicroQuests(questsRes.data);

        // Fetch recent applications (top 5)
        const appsRes = await api.get('/applications');
        setRecentApplications(appsRes.data.applications.slice(0, 5));
      } catch (error) {
        toast.error(error.response?.data?.error || 'Failed to fetch dashboard data.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [user]);

  const handleCompleteQuest = async (questId) => {
    try {
      await api.post(`/goals/micro-quests/${questId}/complete`);
      toast.success('Quest completed! Points added to your streak.');
      // Refresh micro-quests and streak
      const questsRes = await api.get('/goals/micro-quests');
      setMicroQuests(questsRes.data);
      const streakRes = await api.get('/goals/streak');
      setStreak(streakRes.data);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to complete quest.');
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
    <Box>
      <Typography variant="h4" gutterBottom>
        Welcome, {user?.name}!
      </Typography>
      {onboardingData?.dream_milestone && (
        <Typography variant="h6" color="text.secondary" gutterBottom>
          Your dream milestone: {onboardingData.dream_milestone}
        </Typography>
      )}

      <Grid container spacing={3} sx={{ mt: 2 }}>
        {/* Weekly Goals Widget */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h5" component="div">
                Weekly Goals
              </Typography>
              {goals ? (
                <>
                  <Typography variant="body1" sx={{ mt: 2 }}>
                    Applications: {goals.goal.applications_current}/{goals.goal.applications_goal}
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={goals.applications_percentage}
                    sx={{ height: 10, borderRadius: 5, mt: 1 }}
                  />
                  <Typography variant="body1" sx={{ mt: 2 }}>
                    Outreach: {goals.goal.outreach_current}/{goals.goal.outreach_goal}
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={goals.outreach_percentage}
                    sx={{ height: 10, borderRadius: 5, mt: 1 }}
                  />
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                    Days remaining this week: {goals.days_remaining}
                  </Typography>
                </>
              ) : (
                <Typography>No goals set for this week.</Typography>
              )}
              <Button
                variant="outlined"
                sx={{ mt: 2 }}
                onClick={() => navigate('/goals')}
              >
                Manage Goals
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* Streak Widget */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h5" component="div">
                Your Streak
              </Typography>
              {streak ? (
                <>
                  <Typography variant="h4" sx={{ mt: 2, fontWeight: 'bold' }}>
                    🔥 {streak.current_streak} Day Streak
                  </Typography>
                  <Typography variant="body1">
                    Longest Streak: {streak.longest_streak} days
                  </Typography>
                  <Typography variant="body1">
                    Total Points: {streak.total_points}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Level {streak.level}: {streak.level_name}{' '}
                    {streak.next_milestone && `(${streak.points_to_next_level} pts to next)`}
                  </Typography>
                </>
              ) : (
                <Typography>Start your streak by logging an activity!</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Micro-Quests Widget */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h5" component="div">
                Micro-Quests
              </Typography>
              {microQuests.length > 0 ? (
                <List>
                  {microQuests.map((quest) => (
                    <ListItem
                      key={quest.id}
                      secondaryAction={
                        <Button
                          variant="contained"
                          size="small"
                          onClick={() => handleCompleteQuest(quest.id)}
                        >
                          Complete
                        </Button>
                      }
                    >
                      <ListItemText
                        primary={quest.title}
                        secondary={`${quest.points} points - ${quest.description}`}
                      />
                    </ListItem>
                  ))}
                </List>
              ) : (
                <Typography>No micro-quests available at the moment.</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Applications Widget */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h5" component="div">
                Recent Applications
              </Typography>
              {recentApplications.length > 0 ? (
                <List>
                  {recentApplications.map((app) => (
                    <ListItem key={app.id}>
                      <ListItemText
                        primary={app.job_title}
                        secondary={`${app.company_name} - ${app.status}`}
                      />
                    </ListItem>
                  ))}
                </List>
              ) : (
                <Typography>No applications logged yet.</Typography>
              )}
              <Button
                variant="outlined"
                sx={{ mt: 2 }}
                onClick={() => navigate('/applications')}
              >
                View All Applications
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;