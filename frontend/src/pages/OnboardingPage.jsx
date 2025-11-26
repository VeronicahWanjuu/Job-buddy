import { useState } from 'react';
import { Container } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import OnboardingWizard from '../components/onboarding/OnboardingWizard';
import api from '../services/api';

const OnboardingPage = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  const handleComplete = async (formData) => {
    setLoading(true);
    try {
      await api.post('/onboarding', formData);
      toast.success('Onboarding completed successfully! 🎉');
      navigate('/dashboard');
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to complete onboarding');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="lg">
      <OnboardingWizard onComplete={handleComplete} />
    </Container>
  );
};

export default OnboardingPage;