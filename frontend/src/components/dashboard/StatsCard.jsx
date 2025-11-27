import { Paper, Typography, Box, useTheme } from '@mui/material';

const StatsCard = ({ title, value, subtitle, icon, color = 'primary', trend, minHeight, compact }) => {
  const theme = useTheme();
  const colorValue = theme.palette[color]?.main || color;

  return (
    <Paper
      sx={{
        p: compact ? 1.5 : 2,
        height: minHeight ? `${minHeight}px` : '100%',
        minHeight: minHeight ? `${minHeight}px` : 'auto',
        display: 'flex',
        flexDirection: 'column',
        background: `linear-gradient(135deg, ${colorValue}12 0%, ${colorValue}06 100%)`,
        borderLeft: `3px solid`,
        borderLeftColor: colorValue,
        transition: 'transform 0.2s, box-shadow 0.2s',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: 4,
        },
      }}
    >
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flex: 1 }}>
        <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 0.5, textTransform: 'uppercase', fontSize: compact ? '0.6rem' : '0.65rem', fontWeight: 600, letterSpacing: 0.5 }}>
            {title}
          </Typography>
          <Typography variant="h4" sx={{ fontWeight: 700, color: colorValue, lineHeight: 1.2, fontSize: compact ? '1.5rem' : '1.75rem', mb: 0.5 }}>
            {value}
          </Typography>
          {subtitle && (
            <Typography variant="caption" color="text.secondary" sx={{ fontSize: compact ? '0.65rem' : '0.7rem' }}>
              {subtitle}
            </Typography>
          )}
        </Box>
        {icon && (
          <Box
            sx={{
              width: compact ? 28 : 36,
              height: compact ? 28 : 36,
              borderRadius: 1.5,
              bgcolor: `${colorValue}20`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0,
            }}
          >
            {icon}
          </Box>
        )}
      </Box>
      {trend && (
        <Box sx={{ mt: 'auto', pt: 1.5, borderTop: '1px solid', borderColor: 'divider' }}>
          <Typography variant="caption" color={trend > 0 ? 'success.main' : 'text.secondary'}>
            {trend > 0 ? '↑' : '→'} {trend}% from last week
          </Typography>
        </Box>
      )}
    </Paper>
  );
};

export default StatsCard;

