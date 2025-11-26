import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Tabs,
  Tab,
  CircularProgress,
  Button,
  TextField,
  List,
  ListItem,
  ListItemText,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  LinearProgress,
} from '@mui/material';
import { useForm, Controller } from 'react-hook-form';
import { toast } from 'react-toastify';
import api from '../api/axios';

function TabPanel(props) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const CVMatcher = () => {
  const [tabValue, setTabValue] = useState(0);
  const [loading, setLoading] = useState(false);
  const [cvAnalysisResult, setCvAnalysisResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [applications, setApplications] = useState([]);
  const [selectedAnalysis, setSelectedAnalysis] = useState(null);
  const [analysisDetailModalOpen, setAnalysisDetailModalOpen] = useState(false);

  const {
    handleSubmit,
    control,
    reset,
    formState: { errors, isSubmitting },
    watch,
  } = useForm({
    defaultValues: {
      cv_file: null,
      jd_text: '',
      jd_file: null,
      application_id: '',
    },
  });

  const cvFile = watch('cv_file');
  const jdText = watch('jd_text');
  const jdFile = watch('jd_file');

  useEffect(() => {
    fetchApplications();
    fetchHistory();
  }, []);

  const fetchApplications = async () => {
    try {
      const response = await api.get('/applications');
      setApplications(response.data.applications);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to fetch applications.');
    }
  };

  const fetchHistory = async () => {
    try {
      const response = await api.get('/cv/history');
      setHistory(response.data);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to fetch CV analysis history.');
    }
  };

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
    if (newValue === 1) {
      fetchHistory(); // Refresh history when tab is opened
    }
  };

  const handleAnalyzeSubmit = async (data) => {
    setLoading(true);
    try {
      const formData = new FormData();
      if (data.cv_file && data.cv_file.length > 0) {
        // Client-side file size validation (5MB)
        if (data.cv_file[0].size > 5 * 1024 * 1024) {
          toast.error('CV file size exceeds 5MB limit.');
          setLoading(false);
          return;
        }
        formData.append('cv_file', data.cv_file[0]);
      } else {
        toast.error('Please upload a CV file.');
        setLoading(false);
        return;
      }

      if (data.jd_text) {
        formData.append('jd_text', data.jd_text);
      } else if (data.jd_file && data.jd_file.length > 0) {
        formData.append('jd_file', data.jd_file[0]);
      } else {
        toast.error('Please provide a Job Description (text or file).');
        setLoading(false);
        return;
      }

      if (data.application_id) {
        formData.append('application_id', data.application_id);
      }

      const response = await api.post('/cv/analyze', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setCvAnalysisResult(response.data);
      toast.success('CV analyzed successfully!');
      reset(); // Clear form after successful submission
      fetchHistory(); // Refresh history
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to analyze CV.');
    } finally {
      setLoading(false);
    }
  };

  const viewAnalysisDetails = async (analysisId) => {
    try {
      const response = await api.get(`/cv/analysis/${analysisId}`);
      setSelectedAnalysis(response.data);
      setAnalysisDetailModalOpen(true);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to fetch analysis details.');
    }
  };

  return (
    <Container maxWidth="lg">
      <Typography variant="h4" component="h1" gutterBottom>
        CV Matcher & Analyzer
      </Typography>

      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={tabValue} onChange={handleTabChange} aria-label="cv matcher tabs">
          <Tab label="Analyze CV" />
          <Tab label="Analysis History" />
        </Tabs>
      </Box>

      <TabPanel value={tabValue} index={0}>
        <Box component="form" onSubmit={handleSubmit(handleAnalyzeSubmit)} sx={{ mt: 2 }}>
          <Typography variant="h6" gutterBottom>
            Upload your CV (PDF, DOCX)
          </Typography>
          <Controller
            name="cv_file"
            control={control}
            render={({ field: { onChange, value, ...field } }) => (
              <TextField
                {...field}
                type="file"
                fullWidth
                margin="normal"
                InputLabelProps={{ shrink: true }}
                inputProps={{ accept: '.pdf,.docx,.doc' }}
                onChange={(e) => onChange(e.target.files)}
                error={!!errors.cv_file}
                helperText={errors.cv_file?.message}
              />
            )}
          />
          {cvFile && cvFile[0] && (
            <Typography variant="body2" color="text.secondary">
              Selected CV: {cvFile[0].name} ({(cvFile[0].size / (1024 * 1024)).toFixed(2)} MB)
            </Typography>
          )}

          <Typography variant="h6" gutterBottom sx={{ mt: 4 }}>
            Provide Job Description
          </Typography>
          <Controller
            name="jd_text"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                label="Job Description Text"
                multiline
                rows={8}
                fullWidth
                margin="normal"
                disabled={jdFile && jdFile.length > 0} // Disable if JD file is selected
                error={!!errors.jd_text}
                helperText={errors.jd_text?.message || 'Enter job description or upload a file below.'}
              />
            )}
          />
          <Typography variant="body2" align="center" sx={{ my: 1 }}>
            OR
          </Typography>
          <Controller
            name="jd_file"
            control={control}
            render={({ field: { onChange, value, ...field } }) => (
              <TextField
                {...field}
                type="file"
                fullWidth
                margin="normal"
                InputLabelProps={{ shrink: true }}
                inputProps={{ accept: '.pdf,.docx,.doc,.txt' }}
                onChange={(e) => onChange(e.target.files)}
                disabled={jdText.length > 0} // Disable if JD text is entered
                error={!!errors.jd_file}
                helperText={errors.jd_file?.message}
              />
            )}
          />
          {jdFile && jdFile[0] && (
            <Typography variant="body2" color="text.secondary">
              Selected JD File: {jdFile[0].name}
            </Typography>
          )}

          <Typography variant="h6" gutterBottom sx={{ mt: 4 }}>
            Link to Application (Optional)
          </Typography>
          <FormControl fullWidth margin="normal">
            <InputLabel id="application-label">Application</InputLabel>
            <Controller
              name="application_id"
              control={control}
              render={({ field }) => (
                <Select {...field} labelId="application-label" label="Application">
                  <MenuItem value="">
                    <em>None</em>
                  </MenuItem>
                  {applications.map((app) => (
                    <MenuItem key={app.id} value={app.id}>
                      {app.job_title} at {app.company_name}
                    </MenuItem>
                  ))}
                </Select>
              )}
            />
          </FormControl>

          <Button
            type="submit"
            variant="contained"
            color="primary"
            sx={{ mt: 4 }}
            disabled={isSubmitting || loading}
          >
            {isSubmitting || loading ? <CircularProgress size={24} /> : 'Analyze CV'}
          </Button>
        </Box>

        {cvAnalysisResult && (
          <Box sx={{ mt: 5, p: 3, boxShadow: 3, borderRadius: 2 }}>
            <Typography variant="h5" gutterBottom>
              Analysis Result (ATS Score: {cvAnalysisResult.ats_score}%)
            </Typography>
            <LinearProgress
              variant="determinate"
              value={cvAnalysisResult.ats_score}
              color={
                cvAnalysisResult.ats_score >= 80 ? 'success' :
                cvAnalysisResult.ats_score >= 60 ? 'info' :
                cvAnalysisResult.ats_score >= 40 ? 'warning' : 'error'
              }
              sx={{ height: 10, borderRadius: 5, mb: 2 }}
            />

            <Typography variant="h6" sx={{ mt: 3 }}>
              Matched Keywords:
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 1 }}>
              {cvAnalysisResult.matched_keywords.map((keyword, index) => (
                <Chip key={index} label={keyword} color="success" size="small" />
              ))}
            </Box>

            <Typography variant="h6" sx={{ mt: 3 }}>
              Missing Keywords:
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 1 }}>
              {cvAnalysisResult.missing_keywords.map((keyword, index) => (
                <Chip key={index} label={keyword} color="error" size="small" />
              ))}
            </Box>

            <Typography variant="h6" sx={{ mt: 3 }}>
              Suggestions:
            </Typography>
            <List>
              {cvAnalysisResult.suggestions.map((s, index) => (
                <ListItem key={index}>
                  <ListItemText primary={s.suggestion} secondary={s.category} />
                </ListItem>
              ))}
            </List>
          </Box>
        )}
      </TabPanel>

      <TabPanel value={tabValue} index={1}>
        <Typography variant="h5" component="h2" gutterBottom>
          Analysis History
        </Typography>
        {history.length > 0 ? (
          <List>
            {history.map((analysis) => (
              <ListItem key={analysis.id} secondaryAction={
                <Button variant="outlined" size="small" onClick={() => viewAnalysisDetails(analysis.id)}>
                  View Details
                </Button>
              }>
                <ListItemText
                  primary={`CV: ${analysis.cv_filename} (ATS Score: ${analysis.ats_score}%)`}
                  secondary={`Analyzed on: ${new Date(analysis.created_at).toLocaleDateString()}`}
                />
              </ListItem>
            ))}
          </List>
        ) : (
          <Typography>No analysis history found.</Typography>
        )}
      </TabPanel>

      {/* Analysis Detail Modal */}
      <Dialog open={analysisDetailModalOpen} onClose={() => setAnalysisDetailModalOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>CV Analysis Details</DialogTitle>
        <DialogContent>
          {selectedAnalysis ? (
            <Box>
              <Typography variant="h6">ATS Score: {selectedAnalysis.ats_score}%</Typography>
              <LinearProgress
                variant="determinate"
                value={selectedAnalysis.ats_score}
                color={
                  selectedAnalysis.ats_score >= 80 ? 'success' :
                  selectedAnalysis.ats_score >= 60 ? 'info' :
                  selectedAnalysis.ats_score >= 40 ? 'warning' : 'error'
                }
                sx={{ height: 10, borderRadius: 5, mb: 2 }}
              />
              <Typography variant="body2" color="text.secondary">Analyzed on: {new Date(selectedAnalysis.created_at).toLocaleDateString()}</Typography>
              <Typography variant="body2" color="text.secondary">CV File: {selectedAnalysis.cv_filename}</Typography>

              <Typography variant="h6" sx={{ mt: 3 }}>Job Description:</Typography>
              <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>{selectedAnalysis.job_description}</Typography>

              <Typography variant="h6" sx={{ mt: 3 }}>Matched Keywords:</Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 1 }}>
                {selectedAnalysis.matched_keywords.map((keyword, index) => (
                  <Chip key={index} label={keyword} color="success" size="small" />
                ))}
              </Box>

              <Typography variant="h6" sx={{ mt: 3 }}>Missing Keywords:</Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 1 }}>
                {selectedAnalysis.missing_keywords.map((keyword, index) => (
                  <Chip key={index} label={keyword} color="error" size="small" />
                ))}
              </Box>

              <Typography variant="h6" sx={{ mt: 3 }}>Suggestions:</Typography>
              <List>
                {selectedAnalysis.suggestions.map((s, index) => (
                  <ListItem key={index}>
                    <ListItemText primary={s.suggestion} secondary={s.category} />
                  </ListItem>
                ))}
              </List>
            </Box>
          ) : (
            <CircularProgress />
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAnalysisDetailModalOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default CVMatcher;