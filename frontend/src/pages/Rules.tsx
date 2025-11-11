import { useQuery } from 'react-query'
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
  Button,
  Switch,
} from '@mui/material'
import { Add as AddIcon } from '@mui/icons-material'
import { rulesApi } from '../services/api'
import { format } from 'date-fns'

export default function Rules() {
  const { data: rules, isLoading, error } = useQuery('rules', () =>
    rulesApi.getRules().then((res) => res.data)
  )

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    )
  }

  if (error) {
    return <Alert severity="error">Failed to load monitoring rules</Alert>
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4">Monitoring Rules</Typography>
        <Button variant="contained" startIcon={<AddIcon />}>
          Create Rule
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Severity</TableCell>
              <TableCell>Matches</TableCell>
              <TableCell>Alerts</TableCell>
              <TableCell>Last Triggered</TableCell>
              <TableCell>Created</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {rules && rules.length > 0 ? (
              rules.map((rule: any) => (
                <TableRow key={rule.id}>
                  <TableCell>
                    <Typography variant="body2" fontWeight="medium">
                      {rule.name}
                    </Typography>
                    {rule.description && (
                      <Typography variant="caption" color="text.secondary">
                        {rule.description}
                      </Typography>
                    )}
                  </TableCell>
                  <TableCell>
                    <Chip label={rule.severity} size="small" />
                  </TableCell>
                  <TableCell>{rule.total_matches}</TableCell>
                  <TableCell>{rule.total_alerts}</TableCell>
                  <TableCell>
                    {rule.last_triggered
                      ? format(new Date(rule.last_triggered), 'MMM d, yyyy HH:mm')
                      : 'Never'}
                  </TableCell>
                  <TableCell>{format(new Date(rule.created_at), 'MMM d, yyyy')}</TableCell>
                  <TableCell>
                    {rule.enabled ? (
                      <Chip label="Enabled" color="success" size="small" />
                    ) : (
                      <Chip label="Disabled" color="default" size="small" />
                    )}
                  </TableCell>
                  <TableCell>
                    <Switch checked={rule.enabled} size="small" />
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={8} align="center">
                  No monitoring rules found
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  )
}
