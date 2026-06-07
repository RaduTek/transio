import { AppBar, IconButton, Stack, Toolbar, Typography } from '@mui/material'
import { createFileRoute, useRouter } from '@tanstack/react-router'
import ArrowBackIcon from '@mui/icons-material/ArrowBack';

export const Route = createFileRoute('/(testing)/systeminfo')({
  component: RouteComponent,
})

function RouteComponent() {
  const router = useRouter()

  const sysinfo = `=======================
Browser Information:
  User Agent: ${navigator.userAgent}
  Platform: ${navigator.platform}
  Screen Size: ${window.screen.width}x${window.screen.height}
=======================
Application Information:
  App Version: 1.0.0
  Environment: ${import.meta.env.MODE}
=======================
`

  return <Stack sx={{ height: '100%' }}>
    <AppBar position='sticky'>
      <Toolbar>
        <IconButton edge='start' color='inherit' onClick={() => router.history.back()}>
          <ArrowBackIcon />
        </IconButton>
        <Typography variant='h6'>System Info</Typography>
      </Toolbar>
    </AppBar>
    <Stack sx={{ flex: 1, overflowY: 'auto', p: 1 }} spacing={1}>
      <Typography variant='body1' sx={{ whiteSpace: 'pre-wrap' }}>{sysinfo}</Typography>
    </Stack>
  </Stack>
}
