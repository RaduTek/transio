import {
    Alert,
    Box,
    Button,
    Card,
    CardContent,
    CircularProgress,
    TextField,
    Typography,
} from '@mui/material'
import { createFileRoute, useRouter } from '@tanstack/react-router'
import { useMutation } from '@tanstack/react-query'
import { useForm } from '@tanstack/react-form'
import { saveToken } from '../../../helpers/auth'
import { fetchApi, postJSON } from '../../../helpers/net'
import type { Employee } from '../../../types/users'

export const Route = createFileRoute('/_auth/login')({
    component: LoginPage,
})

interface LoginResponse {
    employee: Employee
    token: string
}

async function loginRequest(email: string, password: string): Promise<LoginResponse> {
    const response = await fetchApi('/admin/login', postJSON({ email, password }))
    if (!response.ok) {
        const error = await response.json().catch(() => ({}))
        throw new Error(error?.detail ?? 'Login failed')
    }
    return response.json()
}

// eslint-disable-next-line react-refresh/only-export-components
function LoginPage() {
    const router = useRouter()

    const mutation = useMutation({
        mutationFn: ({ email, password }: { email: string; password: string }) =>
            loginRequest(email, password),
        onSuccess: ({ token }) => {
            saveToken(token)
            router.navigate({ to: '/' })
        },
    })

    const form = useForm({
        defaultValues: { email: '', password: '' },
        onSubmit: ({ value }) => mutation.mutate(value),
    })

    return (
        <Box
            sx={{
                minHeight: '100vh',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                bgcolor: 'grey.100',
            }}
        >
            <Card sx={{ width: '100%', maxWidth: 420 }} elevation={3}>
                <CardContent sx={{ p: 4 }}>
                    <Typography variant="h5" component="h1" fontWeight={600} mb={1}>
                        Admin Dashboard
                    </Typography>
                    <Typography variant="body2" color="text.secondary" mb={3}>
                        Sign in to your account
                    </Typography>

                    {mutation.isError && (
                        <Alert severity="error" sx={{ mb: 2 }}>
                            {mutation.error.message}
                        </Alert>
                    )}

                    <Box
                        component="form"
                        onSubmit={(e) => {
                            e.preventDefault()
                            form.handleSubmit()
                        }}
                        noValidate
                        sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}
                    >
                        <form.Field name="email">
                            {(field) => (
                                <TextField
                                    label="Email"
                                    type="email"
                                    autoComplete="email"
                                    required
                                    fullWidth
                                    value={field.state.value}
                                    onChange={(e) => field.handleChange(e.target.value)}
                                    onBlur={field.handleBlur}
                                    disabled={mutation.isPending}
                                />
                            )}
                        </form.Field>

                        <form.Field name="password">
                            {(field) => (
                                <TextField
                                    label="Password"
                                    type="password"
                                    autoComplete="current-password"
                                    required
                                    fullWidth
                                    value={field.state.value}
                                    onChange={(e) => field.handleChange(e.target.value)}
                                    onBlur={field.handleBlur}
                                    disabled={mutation.isPending}
                                />
                            )}
                        </form.Field>

                        <Button
                            type="submit"
                            variant="contained"
                            size="large"
                            fullWidth
                            disabled={mutation.isPending}
                            sx={{ mt: 1 }}
                        >
                            {mutation.isPending ? <CircularProgress size={24} color="inherit" /> : 'Sign In'}
                        </Button>
                    </Box>
                </CardContent>
            </Card>
        </Box>
    )
}
