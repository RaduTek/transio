import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/validatorMain')({
  component: RouteComponent,
})

function RouteComponent() {
  return <div>Hello "/validatorMain"!</div>
}
