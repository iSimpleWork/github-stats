import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Tab, 
  Tabs, 
  Typography, 
  Paper, 
  List, 
  ListItem, 
  ListItemText,
  ListItemSecondaryAction,
  Chip
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import config from '../config';

function TabPanel({ children, value, index }) {
  return (
    <div hidden={value !== index} role="tabpanel">
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

function Home() {
  const [value, setValue] = useState(0);
  const [dailyTrending, setDailyTrending] = useState([]);
  const [weeklyTrending, setWeeklyTrending] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [dailyRes, weeklyRes] = await Promise.all([
          axios.get(`${config.apiBaseUrl}/api/trending/daily`),
          axios.get(`${config.apiBaseUrl}/api/trending/weekly`)
        ]);
        setDailyTrending(dailyRes.data);
        setWeeklyTrending(weeklyRes.data);
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchData();
  }, []);

  const handleChange = (event, newValue) => {
    setValue(newValue);
  };

  const handleRepositoryClick = (id) => {
    navigate(`/repository/${id}`);
  };

  const renderRepositoryList = (repositories) => (
    <List>
      {repositories.map((repo) => (
        <Paper 
          key={repo.id} 
          elevation={2} 
          sx={{ mb: 2, '&:hover': { backgroundColor: 'action.hover' } }}
        >
          <ListItem 
            button 
            onClick={() => handleRepositoryClick(repo.id)}
          >
            <ListItemText
              primary={repo.full_name}
              secondary={repo.description}
            />
            <ListItemSecondaryAction>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Chip label={`⭐ ${repo.stars}`} size="small" />
                <Chip label={`🔱 ${repo.forks}`} size="small" />
                <Chip label={`👀 ${repo.watchers}`} size="small" />
              </Box>
            </ListItemSecondaryAction>
          </ListItem>
        </Paper>
      ))}
    </List>
  );

  return (
    <Box sx={{ width: '100%' }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Trending Repositories
      </Typography>
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={value} onChange={handleChange}>
          <Tab label="Daily Trending" />
          <Tab label="Weekly Growth" />
        </Tabs>
      </Box>
      <TabPanel value={value} index={0}>
        {renderRepositoryList(dailyTrending)}
      </TabPanel>
      <TabPanel value={value} index={1}>
        {renderRepositoryList(weeklyTrending)}
      </TabPanel>
    </Box>
  );
}

export default Home;
