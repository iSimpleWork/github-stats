import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { 
  Box, 
  Typography, 
  Paper, 
  Grid,
  Link,
  Chip
} from '@mui/material';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend,
  ResponsiveContainer 
} from 'recharts';
import axios from 'axios';
import config from '../config';

function RepositoryDetail() {
  const { id } = useParams();
  const [repository, setRepository] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get(`${config.apiBaseUrl}/api/repository/${id}`);
        setRepository(response.data);
      } catch (error) {
        console.error('Error fetching repository data:', error);
      }
    };

    fetchData();
  }, [id]);

  if (!repository) {
    return <Typography>Loading...</Typography>;
  }

  return (
    <Box>
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          {repository.full_name}
        </Typography>
        <Typography variant="body1" paragraph>
          {repository.description}
        </Typography>
        <Link href={repository.url} target="_blank" rel="noopener noreferrer">
          View on GitHub
        </Link>
        <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
          <Chip label={`⭐ ${repository.stars} stars`} />
          <Chip label={`🔱 ${repository.forks} forks`} />
          <Chip label={`👀 ${repository.watchers} watchers`} />
        </Box>
      </Paper>

      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Statistics History
            </Typography>
            <ResponsiveContainer width="100%" height={400}>
              <LineChart
                data={repository.history}
                margin={{
                  top: 5,
                  right: 30,
                  left: 20,
                  bottom: 5,
                }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="date" 
                  tick={{ fontSize: 12 }}
                  tickFormatter={(value) => new Date(value).toLocaleDateString()}
                />
                <YAxis />
                <Tooltip 
                  labelFormatter={(value) => new Date(value).toLocaleDateString()}
                />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="stars" 
                  stroke="#FFD700" 
                  name="Stars"
                />
                <Line 
                  type="monotone" 
                  dataKey="forks" 
                  stroke="#40E0D0" 
                  name="Forks"
                />
                <Line 
                  type="monotone" 
                  dataKey="watchers" 
                  stroke="#FF69B4" 
                  name="Watchers"
                />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

export default RepositoryDetail;
