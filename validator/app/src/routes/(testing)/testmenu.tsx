import { Alert, AppBar, Button, Stack, Toolbar, Typography } from '@mui/material'
import { createFileRoute, Link as RouterLink } from '@tanstack/react-router'

export const Route = createFileRoute('/(testing)/testmenu')({
  component: RouteComponent,
})

function RouteComponent() {

  const devMode = import.meta.env.DEV

  return <Stack sx={{ height: '100%' }}>
    <AppBar position='sticky'>
      <Toolbar>
        <Typography variant='h6'>Validator Test Menu</Typography>
      </Toolbar>
    </AppBar>
    <Stack sx={{ flex: 1, overflowY: 'auto', p: 1 }} spacing={1}>
      {devMode && <Alert color='info' icon={false}>You can enter this menu by tapping 3 fingers on the screen.</Alert>}
      <Button variant="contained" component={RouterLink} to="/systeminfo">
        System Info
      </Button>
      <Button variant="contained" component={RouterLink} to="/registrationscreen">
        Registration Screen
      </Button>
      <Button variant="contained">Button</Button>
      <Button variant="contained">Button</Button>
    </Stack>
  </Stack>
}
