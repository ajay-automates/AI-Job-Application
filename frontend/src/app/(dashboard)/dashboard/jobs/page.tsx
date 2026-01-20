import { createClient } from '@/lib/supabase/server'
import { JobsTable } from '@/components/jobs/JobsTable'
import { JobsFilters } from '@/components/jobs/JobsFilters'
import { Button } from '@/components/ui/button'
import { Plus } from 'lucide-react'

export default async function JobsPage({
  searchParams,
}: {
  searchParams: { [key: string]: string | string[] | undefined }
}) {
  const supabase = await createClient()

  const {
    data: { user },
  } = await supabase.auth.getUser()

  if (!user) {
    return null
  }

  // Get filter params
  const search = searchParams.search as string | undefined
  const location = searchParams.location as string | undefined
  const jobType = searchParams.job_type as string | undefined

  // Build query
  let query = supabase
    .from('jobs')
    .select('*')
    .eq('is_active', true)
    .order('posted_date', { ascending: false })
    .limit(50)

  // Apply filters
  if (search) {
    query = query.or(`title.ilike.%${search}%,company.ilike.%${search}%`)
  }

  if (location) {
    query = query.ilike('location', `%${location}%`)
  }

  if (jobType) {
    query = query.eq('job_type', jobType)
  }

  const { data: jobs } = await query

  // Get matches for this user
  const { data: matches } = await supabase
    .from('job_matches')
    .select('job_id, match_score')
    .eq('user_id', user.id)

  // Create match score map
  const matchScores: { [key: string]: number } = {}
  matches?.forEach((match) => {
    matchScores[match.job_id] = match.match_score
  })

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Job Listings</h1>
          <p className="text-gray-600 mt-1">
            Browse and apply to jobs that match your profile
          </p>
        </div>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Scrape New Jobs
        </Button>
      </div>

      <JobsFilters />

      <JobsTable jobs={jobs || []} matchScores={matchScores} />
    </div>
  )
}
