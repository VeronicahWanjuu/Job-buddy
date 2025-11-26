import { useState, useEffect } from 'react';
import { Container, Grid, Typography } from '@mui/material';
import { useAuth } from '../hooks/useAuth';
import api from '../services/api';
import LoadingSpinner from '../components/common/LoadingSpinner';
import WelcomeWidget from '../components/dashboard/WelcomeWidget';
import WeeklyGoalsWidget from '../components/dashboard/WeeklyGoalsWidget';
import StreakWidget from '../components/dashboard/StreakWidget';
import MicroQuestsWidget from '../components/dashboard/MicroQuestsWidget';
import RecentApplicationsWidget from '../components/dashboard/RecentApplicationsWidget';
import QuickActionsWidget from '../components/dashboard/QuickActionsWidget';

const DashboardPage = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [dashboardData, setDashboardData] = useState({
    goals: null,
    streak: null,
    applications: [],
    onboarding: null,
  });

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [goalsRes, streakRes, applicationsRes, onboardingRes] = await Promise.all([
        api.get('/goals/current'),
        api.get('/goals/streak'),
        api.get('/applications'),
        api.get('/onboarding'),
      ]);

      setDashboardData({
        goals: goalsRes.data.goal,
        streak: streakRes.data,
        applications: applicationsRes.data.applications,
        onboarding: onboardingRes.data,
      });
    } catch (error) {
      console.error('Failed to load dashboard data', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <LoadingSpinner message="Loading your dashboard..." />;
  }

  return (
    <Container maxWidth="lg">
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>

      <Grid container spacing={3}>
        {/* Welcome Widget */}
        <Grid item xs={12}>
          <WelcomeWidget
            userName={user?.name}
            dreamMilestone={dashboardData.onboarding?.dream_milestone || 'Your dream job'}
          />
        </Grid>

        {/* Weekly Goals */}
        <Grid item xs={12} md={6}>
          <WeeklyGoalsWidget goals={dashboardData.goals} />
        </Grid>

        {/* Streak */}
        <Grid item xs={12} md={6}>
          <StreakWidget streak={dashboardData.streak} />
        </Grid>

        {/* Micro Quests */}
        <Grid item xs={12} md={6}>
          <MicroQuestsWidget />
        </Grid>

        {/* Recent Applications */}
        <Grid item xs={12} md={6}>
          <RecentApplicationsWidget applications={dashboardData.applications} />
        </Grid>

        {/* Quick Actions */}
        <Grid item xs={12}>
          <QuickActionsWidget />
        </Grid>
      </Grid>
    </Container>
  );
};

export default DashboardPage;