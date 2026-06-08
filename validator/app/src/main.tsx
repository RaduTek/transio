import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { createMemoryHistory, createRouter, RouterProvider } from '@tanstack/react-router'
import { routeTree } from './routeTree.gen'

import '@fontsource/roboto/300.css'
import '@fontsource/roboto/400.css'
import '@fontsource/roboto/500.css'
import '@fontsource/roboto/700.css'
import { createTheme, ThemeProvider } from '@mui/material'
import { pn532MifareScannerService } from './services/pn532MifareScanner'

const routerHistory = createMemoryHistory()

const router = createRouter({
  history: routerHistory,
  routeTree,
  defaultPreload: 'intent',
  scrollRestoration: true,
})

const theme = createTheme({
  breakpoints: {
    values: {
      xs: 0,
      sm: 1,
      md: 2,
      lg: 9999,
      xl: 9999,
    },
  }
})

pn532MifareScannerService.start()

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ThemeProvider theme={theme}>
      <RouterProvider router={router} />
    </ThemeProvider>
  </StrictMode>,
)
