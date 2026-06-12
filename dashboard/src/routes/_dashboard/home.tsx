import {
    Box,
    Card,
    CardContent,
    CircularProgress,
    Skeleton,
    Typography,
} from '@mui/material'
import DirectionsBusIcon from '@mui/icons-material/DirectionsBus'
import PeopleIcon from '@mui/icons-material/People'
import PersonIcon from '@mui/icons-material/Person'
import ConfirmationNumberIcon from '@mui/icons-material/ConfirmationNumber'
import { createFileRoute } from '@tanstack/react-router'
import { useQuery } from '@tanstack/react-query'
import {
    Bar,
    BarChart,
    CartesianGrid,
    ResponsiveContainer,
    Tooltip,
    XAxis,
    YAxis,
} from 'recharts'
import { fetchWithAuth } from '../../../helpers/net'

export const Route = createFileRoute('/_dashboard/home')({
    component: OverviewPage,
})

interface ShiftHistoryEntry {
    date: string
    count: number
}

interface StatsOverview {
    vehicle_count: number
    employee_count: number
    customer_count: number
    active_issued_ticket_count: number
    shift_history: ShiftHistoryEntry[]
    validation_history: ShiftHistoryEntry[]
}

async function fetchStats(): Promise<StatsOverview> {
    const res = await fetchWithAuth('/admin/stats/overview')
    if (!res.ok) throw new Error('Failed to fetch statistics')
    return res.json()
}

interface StatCardProps {
    label: string
    value: number | undefined
    icon: React.ReactNode
    color: string
    loading: boolean
}

function StatCard({ label, value, icon, color, loading }: StatCardProps) {
    return (
        <Card sx={{ flex: 1, minWidth: 180 }}>
            <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Box
                    sx={{
                        bgcolor: color,
                        color: 'white',
                        borderRadius: 2,
                        p: 1.5,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                    }}
                >
                    {icon}
                </Box>
                <Box>
                    <Typography variant="body2" color="text.secondary">
                        {label}
                    </Typography>
                    {loading ? (
                        <Skeleton width={60} height={36} />
                    ) : (
                        <Typography variant="h4" sx={{ fontWeight: 700 }}>
                            {value?.toLocaleString()}
                        </Typography>
                    )}
                </Box>
            </CardContent>
        </Card>
    )
}

function OverviewPage() {
    const { data, isLoading, isError } = useQuery({
        queryKey: ['stats', 'overview'],
        queryFn: fetchStats,
    })

    return (
        <Box>
            <Typography variant="h5" sx={{ fontWeight: 600, mb: 3 }}>
                Overview
            </Typography>

            {/* Stat cards */}
            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', mb: 4 }}>
                <StatCard
                    label="Vehicles"
                    value={data?.vehicle_count}
                    icon={<DirectionsBusIcon />}
                    color="primary.main"
                    loading={isLoading}
                />
                <StatCard
                    label="Employees"
                    value={data?.employee_count}
                    icon={<PersonIcon />}
                    color="success.main"
                    loading={isLoading}
                />
                <StatCard
                    label="Customers"
                    value={data?.customer_count}
                    icon={<PeopleIcon />}
                    color="secondary.main"
                    loading={isLoading}
                />
                <StatCard
                    label="Active Issued Tickets"
                    value={data?.active_issued_ticket_count}
                    icon={<ConfirmationNumberIcon />}
                    color="warning.main"
                    loading={isLoading}
                />
            </Box>

            {/* Daily charts */}
            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <Card sx={{ flex: 1, minWidth: 320 }}>
                    <CardContent>
                        <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
                            Shifts per Day
                        </Typography>

                        {isLoading && (
                            <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}>
                                <CircularProgress />
                            </Box>
                        )}

                        {isError && (
                            <Typography color="error">Failed to load shift history.</Typography>
                        )}

                        {data && data.shift_history.length === 0 && (
                            <Typography color="text.secondary">No shift data available.</Typography>
                        )}

                        {data && data.shift_history.length > 0 && (
                            <ResponsiveContainer width="100%" height={300}>
                                <BarChart
                                    data={data.shift_history}
                                    margin={{ top: 4, right: 16, left: 0, bottom: 4 }}
                                >
                                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                                    <XAxis
                                        dataKey="date"
                                        tick={{ fontSize: 12 }}
                                        tickLine={false}
                                        axisLine={false}
                                    />
                                    <YAxis
                                        allowDecimals={false}
                                        tick={{ fontSize: 12 }}
                                        tickLine={false}
                                        axisLine={false}
                                    />
                                    <Tooltip
                                        formatter={(value) => [Number(value ?? 0), 'Shifts']}
                                        labelFormatter={(label) => `Date: ${label}`}
                                    />
                                    <Bar dataKey="count" name="Shifts" radius={[4, 4, 0, 0]} fill="#1976d2" />
                                </BarChart>
                            </ResponsiveContainer>
                        )}
                    </CardContent>
                </Card>

                <Card sx={{ flex: 1, minWidth: 320 }}>
                    <CardContent>
                        <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
                            Validations per Day
                        </Typography>

                        {isLoading && (
                            <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}>
                                <CircularProgress />
                            </Box>
                        )}

                        {isError && (
                            <Typography color="error">Failed to load validation history.</Typography>
                        )}

                        {data && data.validation_history.length === 0 && (
                            <Typography color="text.secondary">No validation data available.</Typography>
                        )}

                        {data && data.validation_history.length > 0 && (
                            <ResponsiveContainer width="100%" height={300}>
                                <BarChart
                                    data={data.validation_history}
                                    margin={{ top: 4, right: 16, left: 0, bottom: 4 }}
                                >
                                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                                    <XAxis
                                        dataKey="date"
                                        tick={{ fontSize: 12 }}
                                        tickLine={false}
                                        axisLine={false}
                                    />
                                    <YAxis
                                        allowDecimals={false}
                                        tick={{ fontSize: 12 }}
                                        tickLine={false}
                                        axisLine={false}
                                    />
                                    <Tooltip
                                        formatter={(value) => [Number(value ?? 0), 'Validations']}
                                        labelFormatter={(label) => `Date: ${label}`}
                                    />
                                    <Bar dataKey="count" name="Validations" radius={[4, 4, 0, 0]} fill="#ed6c02" />
                                </BarChart>
                            </ResponsiveContainer>
                        )}
                    </CardContent>
                </Card>
            </Box>
        </Box>
    )
}
