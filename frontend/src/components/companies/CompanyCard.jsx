import {
  Card,
  CardContent,
  CardActions,
  Typography,
  Box,
  IconButton,
  Chip,
} from '@mui/material';
import {
  Business,
  Language,
  LocationOn,
  Edit,
  Delete,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

const CompanyCard = ({ company, onEdit, onDelete }) => {
  const navigate = useNavigate();

  return (
    <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <CardContent sx={{ flexGrow: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'start', mb: 2 }}>
          <Business sx={{ mr: 1, color: 'primary.main', fontSize: 32 }} />
          <Typography variant="h6" component="div">
            {company.name}
          </Typography>
        </Box>

        {company.industry && (
          <Chip label={company.industry} size="small" sx={{ mb: 1 }} />
        )}

        {company.location && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 0.5 }}>
            <LocationOn fontSize="small" color="action" />
            <Typography variant="body2" color="text.secondary">
              {company.location}
            </Typography>
          </Box>
        )}

        {company.website && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <Language fontSize="small" color="action" />
            <Typography
              variant="body2"
              component="a"
              href={company.website}
              target="_blank"
              rel="noopener noreferrer"
              sx={{ color: 'primary.main', textDecoration: 'none' }}
            >
              Website
            </Typography>
          </Box>
        )}

        {company.notes && (
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }} noWrap>
            {company.notes}
          </Typography>
        )}
      </CardContent>

      <CardActions sx={{ justifyContent: 'space-between', px: 2, pb: 2 }}>
        <Typography
          variant="button"
          sx={{ cursor: 'pointer', color: 'primary.main' }}
          onClick={() => navigate(`/companies/${company.id}`)}
        >
          View Details
        </Typography>
        <Box>
          <IconButton size="small" onClick={() => onEdit(company)}>
            <Edit fontSize="small" />
          </IconButton>
          <IconButton size="small" onClick={() => onDelete(company)} color="error">
            <Delete fontSize="small" />
          </IconButton>
        </Box>
      </CardActions>
    </Card>
  );
};

export default CompanyCard;