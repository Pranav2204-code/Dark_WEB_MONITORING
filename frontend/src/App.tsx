import { ThemeProvider, createTheme, CssBaseline } from '@mui/material'
import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Threats from './pages/Threats'
import ThreatDetail from './pages/ThreatDetail'
import Rules from './pages/Rules'

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#90caf9',
    },
    secondary: {
      main: '#f48fb1',
    },
    error: {
      main: '#f44336',
    },
    warning: {
      main: '#ffa726',
    },
    info: {
      main: '#29b6f6',
    },
    success: {
      main: '#66bb6a',
    },
  },
})

function App() {
  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="threats" element={<Threats />} />
          <Route path="threats/:id" element={<ThreatDetail />} />
          <Route path="rules" element={<Rules />} />
        </Route>
      </Routes>
    </ThemeProvider>
  )
}

export default App
