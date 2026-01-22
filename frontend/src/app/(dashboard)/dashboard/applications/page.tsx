import { createClient } from '@/lib/supabase/server'
import { ApplicationsTable } from '@/components/applications/ApplicationsTable'
import { ApplicationsStats } from '@/components/applications/ApplicationsStats'
import { Button } from '@/components/ui/button'
import { Plus } from 'lucide-react'

export default async function ApplicationsPage() {
  const supabase = await createClient()

  const {
    data: { user },
  } = await supabase.auth.getUser()

  if (!user) {
    return null
  }

  // Get all applications
  const { data: applications } = await supabase
    .from('applications')
    .select(`
      *,
      jobs (
        id,
        title,
        company,
        location,
        url
      )
    `)
    .eq('user_id', user.id)
    .order('created_at', { ascending: false })

  // Calculate stats
  const stats = {
    total: applications?.length || 0,
    pending: applications?.filter((a) => a.status === 'pending').length || 0,
    applied: applications?.filter((a) => a.status === 'applied').length || 0,
    interview: applications?.filter((a) => a.status === 'interview').length || 0,
    offer: applications?.filter((a) => a.status === 'offer').length || 0,
    rejected: applications?.filter((a) => a.status === 'rejected').length || 0,
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">My Applications</h1>
          <p className="text-gray-600 mt-1">
            Track and manage your job applications
          </p>
        </div>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          New Application
        </Button>
      </div>

      <ApplicationsStats stats={stats} />

      <ApplicationsTable applications={applications || []} />
    </div>
  )
}
