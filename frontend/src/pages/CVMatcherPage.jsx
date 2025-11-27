import { useState } from 'react';
import { Container, Typography, Box, Tabs, Tab } from '@mui/material';
import CVAnalyzeTab from '../components/cv/CVAnalyzeTab';
import CVHistoryTab from '../components/cv/CVHistoryTab';

const CVMatcherPage = () => {
  const [tabValue, setTabValue] = useState(0);

  const handleViewAnalysis = (analysisId) => {
    console.log('View analysis:', analysisId);
  };

  return (
    <Container maxWidth="lg">
      <Typography 
        variant="h4" 
        gutterBottom
        sx={{ 
          textAlign: 'center',
          textTransform: 'uppercase',
          fontWeight: 700,
          background: 'linear-gradient(135deg, #1e40af 0%, #06b6d4 100%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          letterSpacing: 2,
          mb: 3,
        }}
      >
        CV Matcher
      </Typography>
      <Typography 
        variant="body2" 
        color="text.secondary" 
        sx={{ 
          mb: 3,
          textAlign: 'center',
          maxWidth: 600,
          mx: 'auto',
        }}
      >
        Analyze your CV against job descriptions to improve your ATS score
      </Typography>

      <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)} sx={{ mb: 3 }}>
        <Tab label="Analyze CV" />
        <Tab label="History" />
      </Tabs>

      {tabValue === 0 && <CVAnalyzeTab />}
      {tabValue === 1 && <CVHistoryTab onViewAnalysis={handleViewAnalysis} />}
    </Container>
  );
};

export default CVMatcherPage;