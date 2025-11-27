import { Box } from '@mui/material';
import Navbar from '../components/common/Navbar';
import Sidebar from '../components/common/Sidebar';
import { useState } from 'react';

const DRAWER_WIDTH = 240;

const MainLayout = ({ children }) => {
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <Navbar onMenuClick={handleDrawerToggle} />
      <Sidebar
        drawerWidth={DRAWER_WIDTH}
        mobileOpen={mobileOpen}
        onDrawerToggle={handleDrawerToggle}
      />
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { sm: `calc(100% - ${DRAWER_WIDTH}px)` },
          mt: 8,
          background: 
            'radial-gradient(circle at 20% 50%, rgba(30, 64, 175, 0.05) 0%, transparent 50%), radial-gradient(circle at 80% 80%, rgba(6, 182, 212, 0.05) 0%, transparent 50%), linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%)',
          backgroundAttachment: 'fixed',
          minHeight: '100vh',
        }}
      >
        {children}
      </Box>
    </Box>
  );
};

export default MainLayout;