import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/_protected/turn_in')({
  component: RouteComponent,
})

function RouteComponent() {
  return <div>Hello "/_protected/turn_in"!</div>
}
