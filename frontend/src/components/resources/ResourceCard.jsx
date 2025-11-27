import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  Button,
} from '@mui/material';
import {
  Article,
  Build,
  Description,
  OpenInNew,
  MenuBook,
} from '@mui/icons-material';

const ICON_MAP = {
  article: <Article />,
  tool: <Build />,
  template: <Description />,
};

const ResourceCard = ({ resource }) => {
  const getTagColor = (level) => {
    const colors = {
      'beginner': 'success',
      'intermediate': 'warning',
      'advanced': 'error'
    };
    return colors[level.toLowerCase()] || 'default';
  };

  return (
    <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column', mb: 1 }}>
      <CardContent sx={{ flexGrow: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'start', mb: 2 }}>
          <Box sx={{ mr: 2, color: 'primary.main' }}>
            {ICON_MAP[resource.type] || <Article />}
          </Box>
          <Box sx={{ flex: 1 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
              <MenuBook color="primary" />
              <Typography variant="h6" component="div">
                {resource.title}
              </Typography>
            </Box>
            <Box sx={{ mb: 1 }}>
              <Chip label={resource.category} size="small" sx={{ mr: 1 }} />
              <Chip label={resource.difficulty} size="small" color={getTagColor(resource.difficulty)} />
            </Box>
          </Box>
        </Box>

        <Typography variant="body2" color="text.secondary">
          {resource.description}
        </Typography>
      </CardContent>

      <Box sx={{ p: 2, pt: 0 }}>
        <Button
          fullWidth
          variant="outlined"
          endIcon={<OpenInNew />}
          href={resource.url}
          target="_blank"
          rel="noopener noreferrer"
        >
          View Resource
        </Button>
      </Box>
    </Card>
  );
};

export default ResourceCard;