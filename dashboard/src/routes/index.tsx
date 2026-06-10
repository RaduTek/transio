import { Box, Container, Typography } from '@mui/material'
import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/')({
  component: Index,
})

function Index() {
  return (
    <Container maxWidth="sm">
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '100vh',
          gap: 2,
        }}
      >
        <Typography variant="h3" component="h1">
          Welcome to Dashboard
        </Typography>
        <Typography variant="body1" color="textSecondary">
          Your dashboard is ready to go!
        </Typography>
      </Box>
    </Container>
  )
}
