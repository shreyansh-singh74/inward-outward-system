import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/_protected/other_application')({
  component: RouteComponent,
})

function RouteComponent() {
  return <div>Hello "/_protected/other_application"!</div>
}
