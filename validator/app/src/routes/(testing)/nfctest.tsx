import { AppBar, Button, IconButton, Stack, Toolbar, Typography } from '@mui/material'
import { createFileRoute, useRouter } from '@tanstack/react-router'
import ArrowBackIcon from '@mui/icons-material/ArrowBack'

export const Route = createFileRoute('/(testing)/nfctest')({
  component: RouteComponent,
})

function RouteComponent() {
  const router = useRouter()

  return <Stack sx={{ height: '100%' }}>
    <AppBar position='sticky'>
      <Toolbar>
        <IconButton edge='start' color='inherit' onClick={() => router.history.back()}>
          <ArrowBackIcon />
        </IconButton>
        <Typography variant='h6'>NFC Test (PN532 WebSerial)</Typography>
      </Toolbar>
    </AppBar>
    <Stack sx={{ flex: 1, overflowY: 'auto', p: 1 }} spacing={1}>
      <Button variant="contained">Connect to PN532 NFC (WebSerial)</Button>
      <Button variant="contained">Disconnect from PN532 NFC (WebSerial)</Button>
      {/* <Button variant="contained" component={RouterLink} to="/systeminfo">
        System Info
      </Button>
      <Button variant="contained" component={RouterLink} to="/registrationscreen">
        Registration Screen
      </Button>
      <Button variant="contained" component={RouterLink} to="/nfctest">
        NFC Test (PN532 WebSerial)
      </Button> */}
    </Stack>
  </Stack>
}
