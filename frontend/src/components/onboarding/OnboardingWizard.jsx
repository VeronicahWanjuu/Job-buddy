import { useState } from 'react';
import {
  Box,
  Stepper,
  Step,
  StepLabel,
  Button,
  Paper,
} from '@mui/material';
import Step1Welcome from './Step1Welcome';
import Step2Feeling from './Step2Feeling';
import Step3Dream from './Step3Dream';
import Step4Goals from './Step4Goals';
import Step5Companies from './Step5Companies';
import Step6Review from './Step6Review';
import Step7Celebration from './Step7Celebration';

const steps = [
  'Welcome',
  'How You Feel',
  'Dream Milestone',
  'Weekly Goals',
  'Target Companies',
  'Review',
  'Complete',
];

const OnboardingWizard = ({ onComplete }) => {
  const [activeStep, setActiveStep] = useState(0);
  const [formData, setFormData] = useState({
    current_feeling: '',
    dream_milestone: '',
    weekly_application_goal: 5,
    weekly_outreach_goal: 3,
    companies: [],
  });
  const [errors, setErrors] = useState({});

  const handleNext = () => {
    if (validateStep()) {
      setActiveStep((prev) => prev + 1);
      setErrors({});
    }
  };

  const handleBack = () => {
    setActiveStep((prev) => prev - 1);
    setErrors({});
  };

  const validateStep = () => {
    const newErrors = {};

    if (activeStep === 1 && !formData.current_feeling) {
      newErrors.current_feeling = 'Please select how you feel';
    }

    if (activeStep === 2) {
      if (!formData.dream_milestone || formData.dream_milestone.trim().length < 10) {
        newErrors.dream_milestone = 'Dream milestone must be at least 10 characters';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const renderStepContent = (step) => {
    switch (step) {
      case 0:
        return <Step1Welcome onNext={handleNext} />;
      case 1:
        return <Step2Feeling formData={formData} setFormData={setFormData} />;
      case 2:
        return <Step3Dream formData={formData} setFormData={setFormData} errors={errors} />;
      case 3:
        return <Step4Goals formData={formData} setFormData={setFormData} />;
      case 4:
        return <Step5Companies formData={formData} setFormData={setFormData} />;
      case 5:
        return <Step6Review formData={formData} />;
      case 6:
        return <Step7Celebration onComplete={() => onComplete(formData)} />;
      default:
        return null;
    }
  };

  return (
    <Box sx={{ maxWidth: 800, mx: 'auto', py: 4 }}>
      <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
        {steps.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>

      <Paper elevation={3} sx={{ p: 4, minHeight: 400 }}>
        {renderStepContent(activeStep)}

        {activeStep > 0 && activeStep < 6 && (
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
            <Button onClick={handleBack}>Back</Button>
            <Button variant="contained" onClick={activeStep === 5 ? () => onComplete(formData) : handleNext}>
              {activeStep === 5 ? 'Submit' : 'Next'}
            </Button>
          </Box>
        )}
      </Paper>
    </Box>
  );
};

export default OnboardingWizard;