import {
  Card,
  CardContent,
  Typography,
  Box,
  IconButton,
} from '@mui/material';
import {
  Person,
  Email,
  LinkedIn,
  Edit,
  Delete,
} from '@mui/icons-material';

const ContactCard = ({ contact, onEdit, onDelete }) => {
  return (
    <Card>
      <CardContent>
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'flex-start',
          }}
        >
          {/* LEFT SIDE — CONTACT DETAILS */}
          <Box sx={{ flex: 1 }}>
            {/* Contact Name */}
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
              <Person color="primary" />
              <Typography variant="h6">{contact.name}</Typography>
            </Box>

            {/* Role */}
            {contact.role && (
              <Typography
                variant="body2"
                color="text.secondary"
                gutterBottom
              >
                {contact.role}
              </Typography>
            )}

            {/* Email */}
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

            {/* LinkedIn */}
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

            {/* Notes */}
            {contact.notes && (
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                {contact.notes}
              </Typography>
            )}
          </Box>

          {/* RIGHT SIDE — ACTION BUTTONS */}
          <Box>
            <IconButton size="small" onClick={() => onEdit(contact)}>
              <Edit fontSize="small" />
            </IconButton>

            <IconButton
              size="small"
              onClick={() => onDelete(contact)}
              color="error"
            >
              <Delete fontSize="small" />
            </IconButton>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

export default ContactCard;
