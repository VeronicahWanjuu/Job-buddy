import React, { useState } from 'react';
import {
  Container,
  Box,
  Typography,
  Button,
  Stepper,
  Step,
  StepLabel,
  RadioGroup,
  FormControlLabel,
  Radio,
  TextField,
  Slider,
  CircularProgress,
} from '@mui/material';
import { useForm, Controller } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import api from '../api/axios';

const steps = [
  'Welcome',
  'Current Feeling',
  'Dream Milestone',
  'Weekly Goals',
  'Company List',
  'Review',
  'Celebrate!',
];

const feelings = [
  'Excited and ready',
  'Overwhelmed but motivated',
  'Frustrated and stuck',
  'Just getting started',
];

const Onboarding = () => {
  const [activeStep, setActiveStep] = useState(0);
  const navigate = useNavigate();

  const {
    handleSubmit,
    control,
    watch,
    formState: { errors, isSubmitting },
    getValues,
  } = useForm({
    defaultValues: {
      current_feeling: '',
      dream_milestone: '',
      weekly_application_goal: 5,
      weekly_outreach_goal: 3,
      companies: '', // Store as comma-separated string for now
    },
  });

  const handleNext = () => {
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  const onSubmit = async (data) => {
    try {
      const companiesArray = data.companies
        .split(',')
        .map((name) => name.trim())
        .filter(Boolean)
        .map((name) => ({ name }));

      const submissionData = {
        current_feeling: data.current_feeling,
        dream_milestone: data.dream_milestone,
        weekly_application_goal: data.weekly_application_goal,
        weekly_outreach_goal: data.weekly_outreach_goal,
        companies: companiesArray,
      };

      await api.post('/onboarding', submissionData);
      toast.success('Onboarding completed successfully!');
      handleNext(); // Move to the "Celebrate!" step
      setTimeout(() => navigate('/dashboard'), 3000); // Redirect after a short delay
    } catch (error) {
      toast.error(error.response?.data?.error || 'An error occurred during onboarding.');
    }
  };

  const getStepContent = (step) => {
    switch (step) {
      case 0:
        return (
          <Box>
            <Typography variant="h5" gutterBottom>
              Welcome to JobBuddy!
            </Typography>
            <Typography variant="body1">
              Let's set you up for success in your job search journey.
            </Typography>
          </Box>
        );
      case 1:
        return (
          <Box>
            <Typography variant="h6" gutterBottom>
              How are you feeling about your job search right now?
            </Typography>
            <Controller
              name="current_feeling"
              control={control}
              rules={{ required: 'Please select an option' }}
              render={({ field }) => (
                <RadioGroup {...field}>
                  {feelings.map((feeling) => (
                    <FormControlLabel
                      key={feeling}
                      value={feeling}
                      control={<Radio />}
                      label={feeling}
                    />
                  ))}
                </RadioGroup>
              )}
            />
            {errors.current_feeling && (
              <Typography color="error">{errors.current_feeling.message}</Typography>
            )}
          </Box>
        );
      case 2:
        return (
          <Box>
            <Typography variant="h6" gutterBottom>
              What is your dream milestone you want to achieve?
            </Typography>
            <Controller
              name="dream_milestone"
              control={control}
              rules={{
                required: 'Dream milestone is required',
                minLength: {
                  value: 10,
                  message: 'Milestone must be at least 10 characters',
                },
              }}
              render={({ field }) => (
                <TextField
                  {...field}
                  fullWidth
                  multiline
                  rows={4}
                  variant="outlined"
                  margin="normal"
                  label="E.g., Become a Senior Software Engineer at Google"
                  error={!!errors.dream_milestone}
                  helperText={errors.dream_milestone?.message}
                />
              )}
            />
          </Box>
        );
      case 3:
        return (
          <Box sx={{ width: '100%' }}>
            <Typography variant="h6" gutterBottom>
              Set your weekly goals
            </Typography>
            <Typography id="application-goal-slider" gutterBottom>
              Weekly Applications Goal: {watch('weekly_application_goal')}
            </Typography>
            <Controller
              name="weekly_application_goal"
              control={control}
              render={({ field: { onChange, value } }) => (
                <Slider
                  value={typeof value === 'number' ? value : 0}
                  onChange={(_, newValue) => onChange(newValue)}
                  aria-labelledby="application-goal-slider"
                  valueLabelDisplay="auto"
                  step={1}
                  marks
                  min={1}
                  max={20}
                />
              )}
            />
            <Typography id="outreach-goal-slider" gutterBottom>
              Weekly Outreach Goal: {watch('weekly_outreach_goal')}
            </Typography>
            <Controller
              name="weekly_outreach_goal"
              control={control}
              render={({ field: { onChange, value } }) => (
                <Slider
                  value={typeof value === 'number' ? value : 0}
                  onChange={(_, newValue) => onChange(newValue)}
                  aria-labelledby="outreach-goal-slider"
                  valueLabelDisplay="auto"
                  step={1}
                  marks
                  min={1}
                  max={15}
                />
              )}
            />
          </Box>
        );
      case 4:
        return (
          <Box>
            <Typography variant="h6" gutterBottom>
              Optional: List companies you're interested in (comma-separated)
            </Typography>
            <Controller
              name="companies"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  fullWidth
                  multiline
                  rows={4}
                  variant="outlined"
                  margin="normal"
                  label="E.g., Google, Microsoft, Amazon"
                  helperText="These companies will be added to your list."
                />
              )}
            />
          </Box>
        );
      case 5:
        const values = getValues();
        return (
          <Box>
            <Typography variant="h6" gutterBottom>
              Review your choices
            </Typography>
            <Typography>
              <strong>Feeling:</strong> {values.current_feeling}
            </Typography>
            <Typography>
              <strong>Milestone:</strong> {values.dream_milestone}
            </Typography>
            <Typography>
              <strong>Weekly Applications:</strong> {values.weekly_application_goal}
            </Typography>
            <Typography>
              <strong>Weekly Outreach:</strong> {values.weekly_outreach_goal}
            </Typography>
            <Typography>
              <strong>Companies:</strong> {values.companies || 'None'}
            </Typography>
          </Box>
        );
      case 6:
        return (
          <Box>
            <Typography variant="h5" gutterBottom>
              Congratulations! 🎉
            </Typography>
            <Typography variant="body1">
              You've successfully completed the onboarding. Get ready to crush your job search!
            </Typography>
            <Button
              variant="contained"
              sx={{ mt: 3 }}
              onClick={() => navigate('/dashboard')}
            >
              Go to Dashboard
            </Button>
          </Box>
        );
      default:
        return 'Unknown step';
    }
  };

  return (
    <Container component="main" maxWidth="md">
      <Box
        sx={{
          marginTop: 4,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          p: 3,
          boxShadow: 3,
          borderRadius: 2,
          bgcolor: 'background.paper',
        }}
      >
        <Stepper activeStep={activeStep} alternativeLabel sx={{ width: '100%', mb: 4 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        <Box sx={{ width: '100%', minHeight: '300px' }}>
          {activeStep === steps.length - 1 ? (
            getStepContent(activeStep)
          ) : (
            <form onSubmit={handleSubmit(onSubmit)}>
              {getStepContent(activeStep)}
              <Box sx={{ display: 'flex', flexDirection: 'row', pt: 2 }}>
                <Button
                  color="inherit"
                  disabled={activeStep === 0 || activeStep === steps.length -1}
                  onClick={handleBack}
                  sx={{ mr: 1 }}
                >
                  Back
                </Button>
                <Box sx={{ flex: '1 1 auto' }} />
                <Button
                  variant="contained"
                  onClick={activeStep === steps.length - 2 ? handleSubmit(onSubmit) : handleNext}
                  disabled={isSubmitting}
                >
                  {isSubmitting ? (
                    <CircularProgress size={24} />
                  ) : activeStep === steps.length - 2 ? (
                    'Finish'
                  ) : (
                    'Next'
                  )}
                </Button>
              </Box>
            </form>
          )}
        </Box>
      </Box>
    </Container>
  );
};

export default Onboarding;