import { createFileRoute, Navigate } from '@tanstack/react-router'
import { useAtomValue } from 'jotai'
import { testModeAtom } from '../atoms'

export const Route = createFileRoute('/')({
  component: RouteComponent,
})

function RouteComponent() {
  const testMode = useAtomValue(testModeAtom)

  if (testMode) {
    console.warn('Running in test mode, redirecting to test menu...')
    return <Navigate to='/testmenu' />
  }

  return <>Hello, World!</>
}
