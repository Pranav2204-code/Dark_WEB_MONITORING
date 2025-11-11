import { useState } from 'react'
import { useQuery } from 'react-query'
import { Link as RouterLink } from 'react-router-dom'
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  CircularProgress,
  Alert,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Grid,
  Button,
} from '@mui/material'
import { threatApi } from '../services/api'
import { format } from 'date-fns'

const severityColors: any = {
  critical: 'error',
  high: 'warning',
  medium: 'info',
  low: 'success',
  info: 'default',
}

export default function Threats() {
  const [severity, setSeverity] = useState('')
  const [source, setSource] = useState('')
  const [search, setSearch] = useState('')

  const { data: threats, isLoading, error } = useQuery(['threats', severity, source], () =>
    threatApi
      .getThreats({
        severity: severity || undefined,
        source: source || undefined,
        limit: 50,
      })
      .then((res) => res.data)
  )

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    )
  }

  if (error) {
    return <Alert severity="error">Failed to load threats</Alert>
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Threats
      </Typography>

      {/* Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2}>
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="Search"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search threats..."
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel>Severity</InputLabel>
              <Select value={severity} onChange={(e) => setSeverity(e.target.value)} label="Severity">
                <MenuItem value="">All</MenuItem>
                <MenuItem value="critical">Critical</MenuItem>
                <MenuItem value="high">High</MenuItem>
                <MenuItem value="medium">Medium</MenuItem>
                <MenuItem value="low">Low</MenuItem>
                <MenuItem value="info">Info</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel>Source</InputLabel>
              <Select value={source} onChange={(e) => setSource(e.target.value)} label="Source">
                <MenuItem value="">All</MenuItem>
                <MenuItem value="forum">Forum</MenuItem>
                <MenuItem value="marketplace">Marketplace</MenuItem>
                <MenuItem value="paste_site">Paste Site</MenuItem>
                <MenuItem value="telegram">Telegram</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={2}>
            <Button
              fullWidth
              variant="outlined"
              sx={{ height: '100%' }}
              onClick={() => {
                setSeverity('')
                setSource('')
                setSearch('')
              }}
            >
              Clear Filters
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {/* Threats Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Title</TableCell>
              <TableCell>Severity</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Source</TableCell>
              <TableCell>Discovered</TableCell>
              <TableCell>Status</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {threats && threats.length > 0 ? (
              threats
                .filter((threat: any) =>
                  search
                    ? threat.title.toLowerCase().includes(search.toLowerCase()) ||
                      threat.content.toLowerCase().includes(search.toLowerCase())
                    : true
                )
                .map((threat: any) => (
                  <TableRow
                    key={threat.id}
                    component={RouterLink}
                    to={`/threats/${threat.id}`}
                    sx={{
                      textDecoration: 'none',
                      '&:hover': { bgcolor: 'action.hover', cursor: 'pointer' },
                    }}
                  >
                    <TableCell>
                      <Typography variant="body2" fontWeight="medium">
                        {threat.title}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {threat.content.substring(0, 100)}...
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip label={threat.severity} color={severityColors[threat.severity]} size="small" />
                    </TableCell>
                    <TableCell>{threat.threat_type.replace(/_/g, ' ')}</TableCell>
                    <TableCell>{threat.source}</TableCell>
                    <TableCell>{format(new Date(threat.discovered_at), 'MMM d, yyyy HH:mm')}</TableCell>
                    <TableCell>
                      {threat.reviewed ? (
                        <Chip label="Reviewed" color="success" size="small" />
                      ) : (
                        <Chip label="Pending" color="default" size="small" />
                      )}
                      {threat.false_positive && (
                        <Chip label="False Positive" color="warning" size="small" sx={{ ml: 1 }} />
                      )}
                    </TableCell>
                  </TableRow>
                ))
            ) : (
              <TableRow>
                <TableCell colSpan={6} align="center">
                  No threats found
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  )
}
