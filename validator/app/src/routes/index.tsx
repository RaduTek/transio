import { AppBar, Button, Toolbar, Typography } from '@mui/material'
import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/')({
  component: RouteComponent,
})

function RouteComponent() {
  return <>
    <AppBar position='sticky'>
      <Toolbar>
        <Typography variant='h6'>Validator</Typography>
      </Toolbar>
    </AppBar>
    <Button variant="contained">Button</Button>
  </>
}
