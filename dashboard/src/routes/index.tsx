import { createFileRoute, Navigate } from '@tanstack/react-router'
import { isTokenSaved } from '../../helpers/auth'

export const Route = createFileRoute('/')({
    component: Index,
})

// eslint-disable-next-line react-refresh/only-export-components
function Index() {
    if (isTokenSaved()) {
        return <Navigate to="/home" />
    }

    return <Navigate to="/login" />
}
