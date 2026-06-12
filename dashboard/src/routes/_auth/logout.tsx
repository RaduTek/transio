import { createFileRoute, Navigate } from '@tanstack/react-router'
import { clearToken } from '../../../helpers/auth'

export const Route = createFileRoute('/_auth/logout')({
    component: RouteComponent,
})

function RouteComponent() {
    clearToken()

    return <Navigate to="/login" />
}
