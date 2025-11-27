import { useState } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  IconButton,
  Button,
} from '@mui/material';
import {
  Person,
  Email,
  LinkedIn,
  Edit,
  Delete,
  Send,
} from '@mui/icons-material';
import GenerateOutreachModal from '../outreach/GenerateOutreachModal';
import LogOutreachModal from '../outreach/LogOutreachModal';

const ContactCard = ({ contact, onEdit, onDelete, onRefresh }) => {
  const [outreachModalOpen, setOutreachModalOpen] = useState(false);
  const [logModalOpen, setLogModalOpen] = useState(false);
  const [prefilledData, setPrefilledData] = useState(null);

  const handleOutreachGenerated = (data) => {
    setOutreachModalOpen(false);
    if (data) {
      setPrefilledData(data);
      setLogModalOpen(true);
    }
  };

  const handleOutreachLogged = () => {
    setLogModalOpen(false);
    setPrefilledData(null);
    if (onRefresh) {
      onRefresh();
    }
  };

  return (
    <>
      <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
        <CardContent sx={{ flexGrow: 1 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 2 }}>
            <Box sx={{ flex: 1 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <Person color="primary" />
                <Typography variant="h6">{contact.name}</Typography>
              </Box>

              {contact.role && (
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  {contact.role}
                </Typography>
              )}

              {contact.email && (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 0.5 }}>
                  <Email fontSize="small" color="action" />
                  <Typography
                    variant="body2"
                    component="a"
                    href={`mailto:${contact.email}`}
                    sx={{ color: 'primary.main', textDecoration: 'none' }}
                  >
                    {contact.email}
                  </Typography>
                </Box>
              )}

              {contact.linkedin_url && (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  <LinkedIn fontSize="small" color="action" />
                  <Typography
                    variant="body2"
                    component="a"
                    href={contact.linkedin_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    sx={{ color: 'primary.main', textDecoration: 'none' }}
                  >
                    LinkedIn
                  </Typography>
                </Box>
              )}

              {contact.notes && (
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  {contact.notes}
                </Typography>
              )}
            </Box>

            <Box>
              <IconButton size="small" onClick={() => onEdit(contact)}>
                <Edit fontSize="small" />
              </IconButton>
              <IconButton size="small" onClick={() => onDelete(contact)} color="error">
                <Delete fontSize="small" />
              </IconButton>
            </Box>
          </Box>

          {/* OUTREACH BUTTON */}
          <Button
            fullWidth
            variant="contained"
            size="small"
            startIcon={<Send />}
            onClick={() => setOutreachModalOpen(true)}
            sx={{ mt: 1 }}
          >
            Generate Outreach
          </Button>
        </CardContent>
      </Card>

      {/* GENERATE OUTREACH MODAL */}
      <GenerateOutreachModal
        open={outreachModalOpen}
        onClose={handleOutreachGenerated}
        contactId={contact.id}
        companyId={contact.company_id}
        applicationId={null}
      />

      {/* LOG OUTREACH MODAL */}
      <LogOutreachModal
        open={logModalOpen}
        onClose={() => {
          setLogModalOpen(false);
          setPrefilledData(null);
        }}
        onSuccess={handleOutreachLogged}
        contactId={contact.id}
        companyId={contact.company_id}
        applicationId={null}
        prefilledData={prefilledData}
      />
    </>
  );
};

export default ContactCard;