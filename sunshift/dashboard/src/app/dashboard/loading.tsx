import { Skeleton } from "@/components/ui/skeleton"
import { Card, CardContent, CardHeader } from "@/components/ui/card"

function CardSkeleton() {
  return (
    <Card className="rounded-xl shadow-sm">
      <CardHeader className="pb-2">
        <Skeleton className="h-4 w-32" />
      </CardHeader>
      <CardContent className="space-y-3">
        <Skeleton className="h-14 w-full rounded-lg" />
        <Skeleton className="h-4 w-3/4" />
        <Skeleton className="h-4 w-1/2" />
      </CardContent>
    </Card>
  )
}

function ChartSkeleton() {
  return (
    <Card className="rounded-xl shadow-sm">
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between">
          <div className="space-y-1.5">
            <Skeleton className="h-5 w-48" />
            <Skeleton className="h-4 w-36" />
          </div>
          <Skeleton className="h-4 w-24" />
        </div>
      </CardHeader>
      <CardContent>
        <Skeleton className="h-64 w-full rounded-xl" />
      </CardContent>
    </Card>
  )
}

export default function DashboardLoading() {
  return (
    <div className="flex min-h-screen flex-col bg-gray-50">
      {/* Header skeleton */}
      <div className="sticky top-0 z-50 w-full border-b border-border bg-white/95 h-14 flex items-center px-4 sm:px-6">
        <div className="mx-auto flex w-full max-w-7xl items-center justify-between">
          <Skeleton className="h-8 w-32 rounded-lg" />
          <Skeleton className="h-4 w-40" />
        </div>
      </div>

      <main className="mx-auto w-full max-w-7xl flex-1 px-4 py-6 sm:px-6 lg:px-8">
        <div className="space-y-5">
          {/* Row 1 */}
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
            <CardSkeleton />
            <CardSkeleton />
          </div>

          {/* Row 2 */}
          <ChartSkeleton />

          {/* Row 3 */}
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
            <CardSkeleton />
            <CardSkeleton />
          </div>
        </div>
      </main>
    </div>
  )
}
