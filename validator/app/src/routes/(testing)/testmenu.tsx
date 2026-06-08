import { AppBar, Button, Stack, Toolbar, Typography } from '@mui/material'
import { createFileRoute, Link as RouterLink } from '@tanstack/react-router'

export const Route = createFileRoute('/(testing)/testmenu')({
  component: RouteComponent,
})

function RouteComponent() {

  return <Stack sx={{ height: '100%' }}>
    <AppBar position='sticky'>
      <Toolbar>
        <Typography variant='h6'>Validator Test Menu</Typography>
      </Toolbar>
    </AppBar>
    <Stack sx={{ flex: 1, overflowY: 'auto', p: 1 }} spacing={1}>
      <Button variant="contained" component={RouterLink} to="/systeminfo">
        System Info
      </Button>
      <Button variant="contained" component={RouterLink} to="/registrationscreen">
        Registration Screen
      </Button>
      <Button variant="contained" component={RouterLink} to="/nfctest">
        NFC Test (PN532 WebSerial)
      </Button>
    </Stack>
  </Stack>
}
