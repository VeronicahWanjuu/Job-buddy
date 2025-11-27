// frontend/src/components/common/Navbar.jsx

import { useState, useEffect } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Badge,
  Box,
  Avatar,
  Menu,
  MenuItem,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Notifications as NotificationsIcon,
  AccountCircle,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { getInitials } from '../../utils/helpers';
import api from '../../services/api';

const Navbar = ({ onMenuClick }) => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [anchorEl, setAnchorEl] = useState(null);
  const [notificationCount, setNotificationCount] = useState(0);

  const fetchUnreadCount = async () => {
    try {
      const response = await api.get('/notifications/unread-count');
      setNotificationCount(response.data.unread_count);
    } catch {
      console.error('Failed to fetch notification count');
    }
  };

  // 🔄 POLL NOTIFICATIONS EVERY 60 SECONDS
  useEffect(() => {
    fetchUnreadCount();
    const intervalId = setInterval(fetchUnreadCount, 60000);
    return () => clearInterval(intervalId);
  }, [fetchUnreadCount]);

  const handleProfileClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleProfile = () => {
    handleClose();
    navigate('/profile');
  };

  const handleLogout = () => {
    handleClose();
    logout();
  };

  return (
    <AppBar
      position="fixed"
      sx={{
        zIndex: (theme) => theme.zIndex.drawer + 1,
        background: 'linear-gradient(135deg, #1e40af 0%, #1e3a8a 100%)',
        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        backgroundColor: '#1e40af !important',
      }}
    >
      <Toolbar sx={{ justifyContent: 'space-between' }}>
        {/* MOBILE MENU BUTTON */}
        <IconButton
          color="inherit"
          edge="start"
          onClick={onMenuClick}
          sx={{ mr: 2, display: { sm: 'none' } }}
        >
          <MenuIcon />
        </IconButton>

        {/* APP TITLE - CENTERED */}
        <Box sx={{ 
          position: 'absolute', 
          left: '50%', 
          transform: 'translateX(-50%)',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          textAlign: 'center'
        }}>
          <Typography 
            variant="h4" 
            component="div" 
            sx={{ 
              fontWeight: 800, 
              letterSpacing: 2,
              fontSize: { xs: '1.5rem', sm: '2rem', md: '2.25rem' },
              color: 'white',
              textShadow: '0 2px 4px rgba(0, 0, 0, 0.3)',
            }}
          >
            {import.meta.env.VITE_APP_NAME || 'JobBuddy'}
          </Typography>
          <Typography 
            variant="body2" 
            sx={{ 
              fontSize: { xs: '0.7rem', sm: '0.85rem' },
              mt: 0.5,
              display: { xs: 'none', sm: 'block' },
              color: 'white',
              fontWeight: 500,
              textShadow: '0 1px 2px rgba(0, 0, 0, 0.3)',
            }}
          >
            Let's get you your dream role
          </Typography>
        </Box>

        {/* ACTIONS: NOTIFICATIONS + PROFILE MENU */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, ml: 'auto' }}>
          {/* NOTIFICATIONS BUTTON */}
          <IconButton
            color="inherit"
            onClick={() => navigate('/notifications')}
          >
            <Badge badgeContent={notificationCount} color="error">
              <NotificationsIcon />
            </Badge>
          </IconButton>

          {/* PROFILE BUTTON */}
          <IconButton color="inherit" onClick={handleProfileClick}>
            {user?.name ? (
              <Avatar
                sx={{ width: 32, height: 32, bgcolor: 'secondary.main' }}
              >
                {getInitials(user.name)}
              </Avatar>
            ) : (
              <AccountCircle />
            )}
          </IconButton>

          {/* PROFILE MENU */}
          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleClose}
          >
            <MenuItem onClick={handleProfile}>Profile</MenuItem>
            <MenuItem onClick={handleLogout}>Logout</MenuItem>
          </Menu>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;
