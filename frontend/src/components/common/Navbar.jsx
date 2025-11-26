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

  // 🔄 POLL NOTIFICATIONS EVERY 60 SECONDS
  useEffect(() => {
    fetchUnreadCount();
    const intervalId = setInterval(fetchUnreadCount, 60000);
    return () => clearInterval(intervalId);
  }, []);

  const fetchUnreadCount = async () => {
    try {
      const response = await api.get('/notifications/unread-count');
      setNotificationCount(response.data.unread_count);
    } catch (error) {
      console.error('Failed to fetch notification count');
    }
  };

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
        backgroundColor: '#1976d2',
      }}
    >
      <Toolbar>
        {/* MOBILE MENU BUTTON */}
        <IconButton
          color="inherit"
          edge="start"
          onClick={onMenuClick}
          sx={{ mr: 2, display: { sm: 'none' } }}
        >
          <MenuIcon />
        </IconButton>

        {/* APP TITLE */}
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          {import.meta.env.VITE_APP_NAME || 'JobBuddy'}
        </Typography>

        {/* ACTIONS: NOTIFICATIONS + PROFILE MENU */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
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
