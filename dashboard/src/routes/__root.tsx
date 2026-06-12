import { CssBaseline, ThemeProvider } from '@mui/material'
import { QueryClientProvider } from '@tanstack/react-query'
import { Outlet, RootRoute } from '@tanstack/react-router'
import { queryClient } from '../config/queryClient'
import { theme } from '../theme'

export const Route = new RootRoute({
    component: RootLayout,
})

function RootLayout() {
    return (
        <QueryClientProvider client={queryClient}>
            <ThemeProvider theme={theme}>
                <CssBaseline />
                <Outlet />
            </ThemeProvider>
        </QueryClientProvider>
    )
}
