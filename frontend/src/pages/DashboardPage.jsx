import { useState, useEffect } from 'react';
import { Container, Grid, Typography, Box, Paper } from '@mui/material';
import {
  Work,
  BusinessCenter,
  CheckCircle,
  Cancel,
  EmojiEvents,
  TrendingUp,
} from '@mui/icons-material';
import { useAuth } from '../hooks/useAuth';
import api from '../services/api';
import LoadingSpinner from '../components/common/LoadingSpinner';
import WelcomeWidget from '../components/dashboard/WelcomeWidget';
import WeeklyGoalsWidget from '../components/dashboard/WeeklyGoalsWidget';
import StreakWidget from '../components/dashboard/StreakWidget';
import MicroQuestsWidget from '../components/dashboard/MicroQuestsWidget';
import RecentApplicationsWidget from '../components/dashboard/RecentApplicationsWidget';
import QuickActionsWidget from '../components/dashboard/QuickActionsWidget';
import StatsCard from '../components/dashboard/StatsCard';
import ActivityFeedWidget from '../components/dashboard/ActivityFeedWidget';
import OutreachWidget from '../components/dashboard/OutreachWidget';

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

  const applications = dashboardData.applications || [];
  const stats = {
    total: applications.length,
    applied: applications.filter((app) => app.status === 'Applied').length,
    interview: applications.filter((app) => app.status === 'Interview').length,
    offer: applications.filter((app) => app.status === 'Offer').length,
    rejected: applications.filter((app) => app.status === 'Rejected').length,
    companies: [...new Set(applications.map((app) => app.company_name))].length,
  };

  return (
    <Container maxWidth="xl" sx={{ py: 2, px: 2 }}>
      <Box sx={{ mb: 2, textAlign: 'center' }}>
        <Typography 
          variant="h4" 
          sx={{ 
            textTransform: 'uppercase',
            fontWeight: 700,
            background: 'linear-gradient(135deg, #1e40af 0%, #06b6d4 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            letterSpacing: 2,
            mb: 1,
            fontFamily: '"Inter", "Roboto", sans-serif',
          }}
        >
          Dashboard
        </Typography>
        <Typography 
          variant="body1" 
          color="text.secondary"
          sx={{ 
            maxWidth: 600,
            mx: 'auto',
            fontFamily: '"Inter", "Roboto", sans-serif',
          }}
        >
          Track your job search progress, goals, and achievements all in one place
        </Typography>
      </Box>

      <Grid container spacing={2} sx={{ mb: 3, alignItems: 'stretch' }}>
        <Grid item xs={12} sm={6} md={4} sx={{ display: 'flex' }}>
          <WelcomeWidget
            userName={user?.name}
            dreamMilestone={dashboardData.onboarding?.dream_milestone || 'Your dream job'}
          />
        </Grid>
        <Grid item xs={6} sm={3} md={2} sx={{ display: 'flex' }}>
          <StatsCard
            title="Total Applications"
            value={stats.total}
            subtitle="All time"
            icon={<Work sx={{ color: 'primary.main', fontSize: 20 }} />}
            color="primary"
            minHeight={120}
            compact
          />
        </Grid>
        <Grid item xs={6} sm={3} md={2} sx={{ display: 'flex' }}>
          <StatsCard
            title="Applied"
            value={stats.applied}
            subtitle="This week"
            icon={<BusinessCenter sx={{ color: 'info.main', fontSize: 20 }} />}
            color="info"
            minHeight={120}
            compact
          />
        </Grid>
        <Grid item xs={6} sm={3} md={2} sx={{ display: 'flex' }}>
          <StatsCard
            title="Interviews"
            value={stats.interview}
            subtitle="Scheduled"
            icon={<TrendingUp sx={{ color: 'warning.main', fontSize: 20 }} />}
            color="warning"
            minHeight={120}
            compact
          />
        </Grid>
        <Grid item xs={6} sm={3} md={2} sx={{ display: 'flex' }}>
          <StatsCard
            title="Offers"
            value={stats.offer}
            subtitle="Received"
            icon={<EmojiEvents sx={{ color: 'success.main', fontSize: 20 }} />}
            color="success"
            minHeight={120}
            compact
          />
        </Grid>
      </Grid>

      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3} sx={{ display: 'flex' }}>
          <Box sx={{ width: '100%' }}>
            <WeeklyGoalsWidget goals={dashboardData.goals} />
          </Box>
        </Grid>
        <Grid item xs={12} sm={6} md={3} sx={{ display: 'flex' }}>
          <Box sx={{ width: '100%' }}>
            <StreakWidget streak={dashboardData.streak} />
          </Box>
        </Grid>
        <Grid item xs={12} sm={6} md={3} sx={{ display: 'flex' }}>
          <Paper sx={{ p: 2, width: '100%', height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', minHeight: 90 }}>
            <Typography variant="body2" gutterBottom sx={{ fontWeight: 600, color: 'text.secondary' }}>
              Total Points
            </Typography>
            <Typography variant="h3" color="primary" sx={{ fontWeight: 700 }}>
              {dashboardData.streak?.total_points || 0}
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={3} sx={{ display: 'flex' }}>
          <OutreachWidget
            outreachGoal={dashboardData.goals?.outreach_goal || 0}
            outreachCurrent={dashboardData.goals?.outreach_current || 0}
          />
        </Grid>
      </Grid>

      <Grid container spacing={2} sx={{ mb: 2 }}>
        <Grid item xs={12}>
          <MicroQuestsWidget />
        </Grid>
      </Grid>

      <Grid container spacing={2} sx={{ mb: 2 }}>
        <Grid item xs={12} md={6}>
          <ActivityFeedWidget applications={applications} />
        </Grid>
        <Grid item xs={12} md={6}>
          <QuickActionsWidget />
        </Grid>
      </Grid>

      <Grid container spacing={2}>
        <Grid item xs={12}>
          <RecentApplicationsWidget applications={applications} />
        </Grid>
      </Grid>
    </Container>
  );
};

export default DashboardPage;