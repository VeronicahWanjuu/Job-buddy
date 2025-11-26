import React, { useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../contexts/AuthContext';
import api from '../api/axios';

import { Badge, IconButton, Box } from '@mui/material';
import NotificationsIcon from '@mui/icons-material/Notifications';

const Navbar = () => {
  const { token } = useContext(AuthContext);
  const navigate = useNavigate();
  const [unreadCount, setUnreadCount] = useState(0);

  const fetchUnreadCount = async () => {
    if (!token) return; // Only fetch if authenticated
    try {
      const res = await api.get('/notifications/unread-count');
      setUnreadCount(res.data.unread_count);
    } catch (error) {
      // Handle error, e.g., token expired, etc.
      console.error("Failed to fetch unread notification count:", error);
    }
  };

  useEffect(() => {
    fetchUnreadCount(); // Initial fetch
    const intervalId = setInterval(fetchUnreadCount, 60000); // Poll every 60 seconds
    return () => clearInterval(intervalId); // Cleanup on unmount
  }, [token]); // Re-run if token changes

  return (
    <nav className="bg-white shadow-md p-4 flex justify-between items-center">
      <div className="container mx-auto">
        <h1 className="text-xl font-bold">JobBuddy</h1>
      </div>
      <Box>
        <IconButton color="inherit" onClick={() => navigate('/notifications')}>
          <Badge badgeContent={unreadCount} color="error">
            <NotificationsIcon />
          </Badge>
        </IconButton>
      </Box>
    </nav>
  );
};

export default Navbar;