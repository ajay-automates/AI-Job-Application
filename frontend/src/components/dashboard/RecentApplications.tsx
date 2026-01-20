import Link from 'next/link'
import { createClient } from '@/lib/supabase/server'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { ArrowRight } from 'lucide-react'

interface RecentApplicationsProps {
  userId: string
}

const statusColors: Record<string, string> = {
  pending: 'bg-yellow-100 text-yellow-800',
  applied: 'bg-blue-100 text-blue-800',
  interview: 'bg-green-100 text-green-800',
  rejected: 'bg-red-100 text-red-800',
  offer: 'bg-purple-100 text-purple-800',
}

export async function RecentApplications({ userId }: RecentApplicationsProps) {
  const supabase = await createClient()

  const { data: applications } = await supabase
    .from('applications')
    .select(`
      *,
      jobs (
        id,
        title,
        company,
        location
      )
    `)
    .eq('user_id', userId)
    .order('created_at', { ascending: false })
    .limit(5)

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Recent Applications</CardTitle>
        <Button variant="ghost" size="sm" asChild>
          <Link href="/dashboard/applications">
            View all
            <ArrowRight className="ml-2 h-4 w-4" />
          </Link>
        </Button>
      </CardHeader>
      <CardContent>
        {!applications || applications.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <p>No applications yet</p>
            <p className="text-sm mt-2">Start applying to jobs to see them here</p>
          </div>
        ) : (
          <div className="space-y-4">
            {applications.map((app: any) => (
              <div
                key={app.id}
                className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50 transition-colors"
              >
                <div className="flex-1">
                  <h4 className="font-medium">{app.jobs?.title || 'Job Title'}</h4>
                  <p className="text-sm text-gray-600">
                    {app.jobs?.company || 'Company'} • {app.jobs?.location || 'Location'}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    Applied {new Date(app.created_at).toLocaleDateString()}
                  </p>
                </div>
                <Badge className={statusColors[app.status] || 'bg-gray-100 text-gray-800'}>
                  {app.status}
                </Badge>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
