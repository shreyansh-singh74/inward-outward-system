import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/_protected/application/$id')({
  component: RouteComponent,
})

function RouteComponent() {
  return <div>Hello "/_protected/application/$id"!</div>
}
