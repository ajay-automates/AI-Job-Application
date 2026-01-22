import { createClient } from '@/lib/supabase/server'
import { StatsCards } from '@/components/dashboard/StatsCards'
import { RecentApplications } from '@/components/dashboard/RecentApplications'
import { TopMatches } from '@/components/dashboard/TopMatches'

export default async function DashboardPage() {
  const supabase = await createClient()

  const {
    data: { user },
  } = await supabase.auth.getUser()

  if (!user) {
    return null
  }

  // Fetch stats
  const { count: totalJobs } = await supabase
    .from('jobs')
    .select('*', { count: 'exact', head: true })
    .eq('is_active', true)

  const { count: totalApplications } = await supabase
    .from('applications')
    .select('*', { count: 'exact', head: true })
    .eq('user_id', user.id)

  const { count: pendingApplications } = await supabase
    .from('applications')
    .select('*', { count: 'exact', head: true })
    .eq('user_id', user.id)
    .in('status', ['pending', 'in_progress'])

  const { count: interviewCount } = await supabase
    .from('applications')
    .select('*', { count: 'exact', head: true })
    .eq('user_id', user.id)
    .eq('status', 'interview')

  const stats = {
    totalJobs: totalJobs || 0,
    totalApplications: totalApplications || 0,
    pendingApplications: pendingApplications || 0,
    interviews: interviewCount || 0,
  }

  return (
    <div className="space-y-6">
      {/* Stats */}
      <StatsCards stats={stats} />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Matched Jobs */}
        <TopMatches userId={user.id} />

        {/* Recent Applications */}
        <RecentApplications userId={user.id} />
      </div>
    </div>
  )
}
