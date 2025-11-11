import { useQuery } from 'react-query'
import {
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  CircularProgress,
  Alert,
} from '@mui/material'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts'
import { threatApi } from '../services/api'

const COLORS = ['#f44336', '#ffa726', '#ffc107', '#29b6f6', '#66bb6a']

export default function Dashboard() {
  const { data: stats, isLoading, error } = useQuery('threat-stats', () =>
    threatApi.getStats(7).then((res) => res.data)
  )

  const { data: threats } = useQuery('recent-threats', () =>
    threatApi.getThreats({ limit: 10 }).then((res) => res.data)
  )

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    )
  }

  if (error) {
    return <Alert severity="error">Failed to load dashboard data</Alert>
  }

  // Prepare chart data
  const severityData = Object.entries(stats?.by_severity || {}).map(([name, value]) => ({
    name,
    value,
  }))

  const typeData = Object.entries(stats?.by_type || {}).map(([name, value]) => ({
    name: name.replace(/_/g, ' '),
    count: value,
  }))

  const sourceData = Object.entries(stats?.by_source || {}).map(([name, value]) => ({
    name,
    count: value,
  }))

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      <Typography variant="subtitle1" color="text.secondary" gutterBottom>
        Dark Web Threat Intelligence Overview (Last 7 Days)
      </Typography>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4, mt: 2 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Total Threats
              </Typography>
              <Typography variant="h4">{stats?.total_threats || 0}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ bgcolor: 'error.dark' }}>
            <CardContent>
              <Typography color="white" gutterBottom>
                Critical Unreviewed
              </Typography>
              <Typography variant="h4" color="white">
                {stats?.critical_unreviewed || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Critical Severity
              </Typography>
              <Typography variant="h4" color="error">
                {stats?.by_severity?.critical || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                High Severity
              </Typography>
              <Typography variant="h4" color="warning.main">
                {stats?.by_severity?.high || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Charts */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Threats by Severity
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={severityData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={(entry) => `${entry.name}: ${entry.value}`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {severityData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Threats by Type
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={typeData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#90caf9" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Threats by Source
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={sourceData} layout="horizontal">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis dataKey="name" type="category" />
                <Tooltip />
                <Legend />
                <Bar dataKey="count" fill="#f48fb1" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Recent Threats */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Recent Threats
            </Typography>
            {threats && threats.length > 0 ? (
              <Box>
                {threats.map((threat: any) => (
                  <Box
                    key={threat.id}
                    sx={{
                      p: 2,
                      mb: 1,
                      border: 1,
                      borderColor: 'divider',
                      borderRadius: 1,
                    }}
                  >
                    <Typography variant="subtitle1" fontWeight="bold">
                      {threat.title}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {threat.content.substring(0, 200)}...
                    </Typography>
                    <Box sx={{ mt: 1, display: 'flex', gap: 2 }}>
                      <Typography variant="caption" color="error">
                        Severity: {threat.severity}
                      </Typography>
                      <Typography variant="caption">Type: {threat.threat_type}</Typography>
                      <Typography variant="caption">Source: {threat.source}</Typography>
                    </Box>
                  </Box>
                ))}
              </Box>
            ) : (
              <Typography color="text.secondary">No recent threats found</Typography>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  )
}
