// frontend/src/components/cv/CVAnalyzeTab.jsx
import { useState } from 'react';
import {
  Box,
  Button,
  TextField,
  Typography,
  Paper,
  Alert,
  LinearProgress,
} from '@mui/material';
import { CloudUpload, Description } from '@mui/icons-material';
import { toast } from 'react-toastify';
import api from '../../services/api';
import ATSScoreGauge from './ATSScoreGauge';
import KeywordsDisplay from './KeywordsDisplay';

const CVAnalyzeTab = () => {
  const [cvFile, setCvFile] = useState(null);
  const [jdText, setJdText] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleFileChange = (e) => {
    const file = e.target.files[0];

    if (file) {
      const validTypes = [
        'application/pdf',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      ];
      const maxSize = 5 * 1024 * 1024; // 5MB

      if (!validTypes.includes(file.type)) {
        toast.error('Only PDF and DOCX files are allowed');
        return;
      }

      if (file.size > maxSize) {
        toast.error('File size must be less than 5MB');
        return;
      }

      setCvFile(file);
    }
  };

  const handleAnalyze = async () => {
    if (!cvFile) {
      toast.error('Please upload your CV');
      return;
    }

    if (!jdText || jdText.trim().length < 50) {
      toast.error('Job description must be at least 50 characters');
      return;
    }

    setLoading(true);

    try {
      const formData = new FormData();
      formData.append('cv_file', cvFile);
      formData.append('jd_text', jdText);

      const response = await api.post('/cv/analyze', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      setResult(response.data);
      toast.success('Analysis complete!');
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to analyze CV');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setCvFile(null);
    setJdText('');
    setResult(null);
  };

  return (
    <Box>
      {!result ? (
        <>
          {/* UPLOAD CV */}
          <Paper variant="outlined" sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Upload Your CV
            </Typography>

            <Button
              variant="contained"
              component="label"
              startIcon={<CloudUpload />}
              sx={{ mb: 2 }}
            >
              Choose File
              <input
                type="file"
                hidden
                accept=".pdf,.docx,.doc"
                onChange={handleFileChange}
              />
            </Button>

            {cvFile && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Description color="primary" />
                <Typography variant="body2">{cvFile.name}</Typography>
              </Box>
            )}
          </Paper>

          {/* JOB DESCRIPTION */}
          <Paper variant="outlined" sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Job Description
            </Typography>

            <TextField
              fullWidth
              multiline
              rows={10}
              placeholder="Paste the job description here..."
              value={jdText}
              onChange={(e) => setJdText(e.target.value)}
            />

            <Typography
              variant="caption"
              color="text.secondary"
              sx={{ mt: 1, display: 'block' }}
            >
              {jdText.length} characters (minimum 50)
            </Typography>
          </Paper>

          {/* ANALYZE BUTTON */}
          <Button
            variant="contained"
            size="large"
            fullWidth
            onClick={handleAnalyze}
            disabled={loading || !cvFile || jdText.length < 50}
          >
            {loading ? 'Analyzing...' : 'Analyze CV'}
          </Button>

          {loading && <LinearProgress sx={{ mt: 2 }} />}
        </>
      ) : (
        <>
          {/* ANALYSIS RESULTS */}
          <Alert severity="success" sx={{ mb: 3 }}>
            Analysis complete! Your ATS score: {result.ats_score}%
          </Alert>

          <ATSScoreGauge score={result.ats_score} />

          <KeywordsDisplay
            matched={result.matched_keywords}
            missing={result.missing_keywords}
          />

          {/* SUGGESTIONS */}
          <Paper sx={{ p: 3, mt: 3 }}>
            <Typography variant="h6" gutterBottom>
              Suggestions for Improvement
            </Typography>

            {result.suggestions.map((suggestion, index) => (
              <Box key={index} sx={{ mb: 2 }}>
                <Typography variant="subtitle2" color="primary">
                  {suggestion.category}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {suggestion.suggestion}
                </Typography>
              </Box>
            ))}
          </Paper>

          <Button
            variant="outlined"
            fullWidth
            sx={{ mt: 3 }}
            onClick={handleReset}
          >
            Analyze Another CV
          </Button>
        </>
      )}
    </Box>
  );
};

export default CVAnalyzeTab;
