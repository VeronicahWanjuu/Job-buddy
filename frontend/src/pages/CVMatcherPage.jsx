// frontend/src/pages/CVMatcherPage.jsx
import { useState } from 'react';
import { Container, Typography, Box, Tabs, Tab } from '@mui/material';
import CVAnalyzeTab from '../components/cv/CVAnalyzeTab';
import CVHistoryTab from '../components/cv/CVHistoryTab';

const CVMatcherPage = () => {
  const [tabValue, setTabValue] = useState(0);

  const handleViewAnalysis = (analysisId) => {
    // TODO: Open analysis detail modal
    console.log('View analysis:', analysisId);
  };

  return (
    <Container maxWidth="lg">
      <Typography variant="h4" gutterBottom>
        CV Matcher
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
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