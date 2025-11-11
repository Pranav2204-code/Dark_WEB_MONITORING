import { useParams } from 'react-router-dom'
import { useQuery } from 'react-query'
import {
  Box,
  Typography,
  Paper,
  Chip,
  CircularProgress,
  Alert,
  Grid,
  Button,
  Divider,
} from '@mui/material'
import { threatApi } from '../services/api'
import { format } from 'date-fns'

export default function ThreatDetail() {
  const { id } = useParams<{ id: string }>()

  const { data: threat, isLoading, error } = useQuery(['threat', id], () =>
    threatApi.getThreat(id!).then((res) => res.data)
  )

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    )
  }

  if (error || !threat) {
    return <Alert severity="error">Failed to load threat details</Alert>
  }

  return (
    <Box>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          {threat.title}
        </Typography>
        <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
          <Chip label={threat.severity} color="error" />
          <Chip label={threat.threat_type.replace(/_/g, ' ')} />
          <Chip label={threat.source} variant="outlined" />
        </Box>
      </Box>

      <Grid container spacing={3}>
        {/* Main Content */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Content
            </Typography>
            <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
              {threat.content}
            </Typography>

            {threat.url && (
              <Box sx={{ mt: 3 }}>
                <Typography variant="subtitle2" color="text.secondary">
                  Source URL:
                </Typography>
                <Typography variant="body2" sx={{ wordBreak: 'break-all' }}>
                  {threat.url}
                </Typography>
              </Box>
            )}
          </Paper>

          {/* Intelligence */}
          {threat.intelligence && (
            <Paper sx={{ p: 3, mt: 3 }}>
              <Typography variant="h6" gutterBottom>
                Threat Intelligence
              </Typography>

              {threat.intelligence.keywords && threat.intelligence.keywords.length > 0 && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Keywords:
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {threat.intelligence.keywords.map((keyword: string, i: number) => (
                      <Chip key={i} label={keyword} size="small" />
                    ))}
                  </Box>
                </Box>
              )}

              {threat.intelligence.iocs && threat.intelligence.iocs.length > 0 && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Indicators of Compromise:
                  </Typography>
                  {threat.intelligence.iocs.map((ioc: any, i: number) => (
                    <Box key={i} sx={{ mb: 1 }}>
                      <Typography variant="caption" color="text.secondary">
                        {ioc.type}:
                      </Typography>
                      <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                        {ioc.value}
                      </Typography>
                    </Box>
                  ))}
                </Box>
              )}

              {threat.intelligence.tags && threat.intelligence.tags.length > 0 && (
                <Box>
                  <Typography variant="subtitle2" gutterBottom>
                    Tags:
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {threat.intelligence.tags.map((tag: string, i: number) => (
                      <Chip key={i} label={tag} size="small" color="primary" />
                    ))}
                  </Box>
                </Box>
              )}
            </Paper>
          )}
        </Grid>

        {/* Metadata Sidebar */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Metadata
            </Typography>
            <Divider sx={{ mb: 2 }} />

            <Box sx={{ mb: 2 }}>
              <Typography variant="caption" color="text.secondary">
                Discovered At
              </Typography>
              <Typography variant="body2">
                {format(new Date(threat.discovered_at), 'MMM d, yyyy HH:mm:ss')}
              </Typography>
            </Box>

            {threat.author && (
              <Box sx={{ mb: 2 }}>
                <Typography variant="caption" color="text.secondary">
                  Author
                </Typography>
                <Typography variant="body2">{threat.author}</Typography>
              </Box>
            )}

            {threat.posted_at && (
              <Box sx={{ mb: 2 }}>
                <Typography variant="caption" color="text.secondary">
                  Posted At
                </Typography>
                <Typography variant="body2">
                  {format(new Date(threat.posted_at), 'MMM d, yyyy HH:mm:ss')}
                </Typography>
              </Box>
            )}

            <Box sx={{ mb: 2 }}>
              <Typography variant="caption" color="text.secondary">
                Source Name
              </Typography>
              <Typography variant="body2">{threat.source_name || 'N/A'}</Typography>
            </Box>

            <Divider sx={{ my: 2 }} />

            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              <Button variant="contained" color="success" fullWidth>
                Mark as Reviewed
              </Button>
              <Button variant="outlined" color="warning" fullWidth>
                Mark as False Positive
              </Button>
              <Button variant="outlined" color="error" fullWidth>
                Delete
              </Button>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  )
}
