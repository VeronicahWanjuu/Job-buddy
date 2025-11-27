import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Box,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Work as WorkIcon,
  Business as BusinessIcon,
  Email as EmailIcon,
  Description as DescriptionIcon,
  School as SchoolIcon,
  People as PeopleIcon,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';

const menuItems = [
  { text: 'Dashboard', icon: <DashboardIcon />, path: '/dashboard' },
  { text: 'Applications', icon: <WorkIcon />, path: '/applications' },
  { text: 'Companies', icon: <BusinessIcon />, path: '/companies' },
  { text: 'CV Matcher', icon: <DescriptionIcon />, path: '/cv-matcher' },
  { text: 'Resources', icon: <SchoolIcon />, path: '/resources' },
  { text: 'Coaches', icon: <PeopleIcon />, path: '/coaches' },
];

const Sidebar = ({ drawerWidth, mobileOpen, onDrawerToggle }) => {
  const navigate = useNavigate();
  const location = useLocation();

  const drawer = (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%', background: 'linear-gradient(180deg, #1e3a8a 0%, #1e40af 100%)' }}>
      <Toolbar />
      <List sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', justifyContent: 'space-around', py: 2 }}>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding sx={{ flex: 1, maxHeight: 'calc((100vh - 64px) / 6)' }}>
            <ListItemButton
              selected={location.pathname === item.path}
              onClick={() => {
                navigate(item.path);
                if (mobileOpen) onDrawerToggle();
              }}
              sx={{
                py: 2,
                height: '100%',
                borderLeft: location.pathname === item.path ? '4px solid' : 'none',
                borderLeftColor: location.pathname === item.path ? '#06b6d4' : 'transparent',
                bgcolor: location.pathname === item.path ? 'rgba(6, 182, 212, 0.15)' : 'transparent',
                color: 'white',
                '&:hover': {
                  bgcolor: 'rgba(255, 255, 255, 0.08)',
                },
                '& .MuiListItemIcon-root': {
                  color: location.pathname === item.path ? '#06b6d4' : 'rgba(255, 255, 255, 0.85)',
                },
                '& .MuiListItemText-primary': {
                  color: 'white',
                  fontWeight: 600,
                }
              }}
            >
              <ListItemIcon sx={{ minWidth: 40, color: location.pathname === item.path ? '#fbbf24' : 'rgba(255, 255, 255, 0.9)' }}>{item.icon}</ListItemIcon>
              <ListItemText 
                primary={item.text} 
                primaryTypographyProps={{ 
                  fontSize: '1rem',
                  fontWeight: location.pathname === item.path ? 700 : 600,
                  color: 'white',
                }}
              />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Box>
  );

  return (
    <Box
      component="nav"
      sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
    >
      {/* Mobile drawer */}
      <Drawer
        variant="temporary"
        open={mobileOpen}
        onClose={onDrawerToggle}
        ModalProps={{ keepMounted: true }}
        sx={{
          display: { xs: 'block', sm: 'none' },
          '& .MuiDrawer-paper': { 
            boxSizing: 'border-box', 
            width: drawerWidth,
            background: 'linear-gradient(180deg, #1e3a8a 0%, #1e40af 100%)',
            borderRight: 'none',
          },
        }}
      >
        {drawer}
      </Drawer>

      {/* Desktop drawer */}
      <Drawer
        variant="permanent"
        sx={{
          display: { xs: 'none', sm: 'block' },
          '& .MuiDrawer-paper': { 
            boxSizing: 'border-box', 
            width: drawerWidth,
            background: 'linear-gradient(180deg, #1e3a8a 0%, #1e40af 100%)',
            borderRight: 'none',
          },
        }}
        open
      >
        {drawer}
      </Drawer>
    </Box>
  );
};

export default Sidebar;