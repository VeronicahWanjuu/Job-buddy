import { Box, Typography, Button } from '@mui/material';
import SearchOffIcon from '@mui/icons-material/SearchOff';

const EmptyState = ({
  icon: IconComponent = SearchOffIcon,
  title = 'No items found',
  message = 'Get started by adding your first item',
  actionLabel,
  onAction,
}) => {
  const Icon = IconComponent;
  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '300px',
        p: 4,
      }}
    >
      <Icon sx={{ fontSize: 80, color: 'text.secondary', mb: 2, opacity: 0.5 }} />
      <Typography variant="h6" color="textSecondary" gutterBottom>
        {title}
      </Typography>
      <Typography variant="body2" color="textSecondary">
        {message}
      </Typography>
      {actionLabel && onAction && (
        <Button variant="contained" onClick={onAction} sx={{ mt: 2 }}>
          {actionLabel}
        </Button>
      )}
    </Box>
  );
};

export default EmptyState;