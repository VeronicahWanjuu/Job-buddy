import { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Button,
  Grid,
  TextField,
  MenuItem,
} from '@mui/material';
import { Add } from '@mui/icons-material';
import { toast } from 'react-toastify';
import api from '../services/api';
import LoadingSpinner from '../components/common/LoadingSpinner';
import EmptyState from '../components/common/EmptyState';
import CompanyCard from '../components/companies/CompanyCard';
import AddCompanyModal from '../components/companies/AddCompanyModal';

const CompaniesPage = () => {
  const [loading, setLoading] = useState(true);
  const [companies, setCompanies] = useState([]);
  const [filteredCompanies, setFilteredCompanies] = useState([]);
  const [addModalOpen, setAddModalOpen] = useState(false);
  const [editCompany, setEditCompany] = useState(null);
  const [industryFilter, setIndustryFilter] = useState('');

  useEffect(() => {
    fetchCompanies();
  }, []);

  useEffect(() => {
    if (industryFilter) {
      setFilteredCompanies(
        companies.filter((c) => c.industry === industryFilter)
      );
    } else {
      setFilteredCompanies(companies);
    }
  }, [industryFilter, companies]);

  const fetchCompanies = async () => {
    setLoading(true);
    try {
      const response = await api.get('/companies');
      setCompanies(response.data);
      setFilteredCompanies(response.data);
    } catch (error) {
      toast.error('Failed to load companies');
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (company) => {
    setEditCompany(company);
    setAddModalOpen(true);
  };

  const handleDelete = async (company) => {
    if (!window.confirm(`Delete ${company.name}? This will also delete all related contacts and applications.`)) {
      return;
    }

    try {
      await api.delete(`/companies/${company.id}`);
      toast.success('Company deleted');
      fetchCompanies();
    } catch (error) {
      toast.error('Failed to delete company');
    }
  };

  const handleModalClose = () => {
    setAddModalOpen(false);
    setEditCompany(null);
  };

  const industries = [...new Set(companies.map((c) => c.industry).filter(Boolean))];

  if (loading) {
    return <LoadingSpinner message="Loading companies..." />;
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Companies</Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setAddModalOpen(true)}
        >
          Add Company
        </Button>
      </Box>

      {companies.length > 0 && (
        <Box sx={{ mb: 3 }}>
          <TextField
            select
            label="Filter by Industry"
            value={industryFilter}
            onChange={(e) => setIndustryFilter(e.target.value)}
            sx={{ minWidth: 200 }}
            size="small"
          >
            <MenuItem value="">All Industries</MenuItem>
            {industries.map((industry) => (
              <MenuItem key={industry} value={industry}>
                {industry}
              </MenuItem>
            ))}
          </TextField>
        </Box>
      )}

      {filteredCompanies.length === 0 ? (
        <EmptyState
          title="No companies found"
          message="Start by adding companies you're interested in"
          actionLabel="Add Your First Company"
          onAction={() => setAddModalOpen(true)}
        />
      ) : (
        <Grid container spacing={3}>
          {filteredCompanies.map((company) => (
            <Grid item xs={12} sm={6} md={4} key={company.id}>
              <CompanyCard
                company={company}
                onEdit={handleEdit}
                onDelete={handleDelete}
              />
            </Grid>
          ))}
        </Grid>
      )}

      <AddCompanyModal
        open={addModalOpen}
        onClose={handleModalClose}
        onSuccess={fetchCompanies}
        editCompany={editCompany}
      />
    </Container>
  );
};

export default CompaniesPage;