import {
    AppBar,
    Box,
    Button,
    Divider,
    Drawer,
    List,
    ListItem,
    ListItemButton,
    ListItemIcon,
    ListItemText,
    Toolbar,
    Typography,
} from '@mui/material'
import DirectionsBusIcon from '@mui/icons-material/DirectionsBus'
import ConfirmationNumberIcon from '@mui/icons-material/ConfirmationNumber'
import BuildIcon from '@mui/icons-material/Build'
import PeopleIcon from '@mui/icons-material/People'
import DashboardIcon from '@mui/icons-material/Dashboard'
import { createFileRoute, Link, Outlet, useRouter, useRouterState } from '@tanstack/react-router'

export const Route = createFileRoute('/_dashboard')({
    component: DashboardLayout,
})

const DRAWER_WIDTH = 240

const navItems = [
    { label: 'Overview', to: '/dashboard/home', icon: <DashboardIcon /> },
    { label: 'Transit', to: '/dashboard/transit', icon: <DirectionsBusIcon /> },
    { label: 'Ticketing', to: '/dashboard/ticketing', icon: <ConfirmationNumberIcon /> },
    { label: 'Assets', to: '/dashboard/assets', icon: <BuildIcon /> },
    { label: 'Users', to: '/dashboard/users', icon: <PeopleIcon /> },
]

function DashboardLayout() {
    const router = useRouter()
    
    const pathname = useRouterState({ select: (s) => s.location.pathname })

    return (
        <Box sx={{ display: 'flex' }}>
            <AppBar
                position="fixed"
                sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}
            >
                <Toolbar>
                    <Typography variant="h6" noWrap component="div">
                        Transio Admin
                    </Typography>
                    <Box sx={{ flexGrow: 1 }} />
                    <Button color="inherit" onClick={() => router.navigate({ to: '/logout' })}>
                        Logout
                    </Button>
                </Toolbar>
            </AppBar>

            <Drawer
                variant="permanent"
                sx={{
                    width: DRAWER_WIDTH,
                    flexShrink: 0,
                    [`& .MuiDrawer-paper`]: {
                        width: DRAWER_WIDTH,
                        boxSizing: 'border-box',
                    },
                }}
            >
                <Toolbar />
                <Divider />
                <List>
                    {navItems.map((item) => {
                        const isActive = pathname === item.to || pathname.startsWith(item.to + '/')
                        return (
                            <ListItem key={item.to} disablePadding>
                                <ListItemButton
                                    component={Link}
                                    to={item.to}
                                    selected={isActive}
                                >
                                    <ListItemIcon
                                        sx={{ color: isActive ? 'primary.main' : 'inherit' }}
                                    >
                                        {item.icon}
                                    </ListItemIcon>
                                    <ListItemText primary={item.label} />
                                </ListItemButton>
                            </ListItem>
                        )
                    })}
                </List>
            </Drawer>

            <Box
                component="main"
                sx={{ flexGrow: 1, p: 3, minHeight: '100vh', bgcolor: 'grey.50' }}
            >
                <Toolbar />
                <Outlet />
            </Box>
        </Box>
    )
}
