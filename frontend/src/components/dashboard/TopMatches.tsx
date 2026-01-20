import Link from 'next/link'
import { createClient } from '@/lib/supabase/server'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { ArrowRight, MapPin, DollarSign } from 'lucide-react'

interface TopMatchesProps {
  userId: string
}

export async function TopMatches({ userId }: TopMatchesProps) {
  const supabase = await createClient()

  const { data: matches } = await supabase
    .from('job_matches')
    .select(`
      *,
      jobs (
        id,
        title,
        company,
        location,
        salary_min,
        salary_max,
        salary_currency,
        job_type
      )
    `)
    .eq('user_id', userId)
    .gte('match_score', 70)
    .order('match_score', { ascending: false })
    .limit(5)

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Top Matches</CardTitle>
        <Button variant="ghost" size="sm" asChild>
          <Link href="/dashboard/jobs">
            View all
            <ArrowRight className="ml-2 h-4 w-4" />
          </Link>
        </Button>
      </CardHeader>
      <CardContent>
        {!matches || matches.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <p>No matches yet</p>
            <p className="text-sm mt-2">Upload your resume to see job matches</p>
            <Button className="mt-4" asChild>
              <Link href="/dashboard/profile">Upload Resume</Link>
            </Button>
          </div>
        ) : (
          <div className="space-y-4">
            {matches.map((match: any) => {
              const job = match.jobs
              const matchColor =
                match.match_score >= 85
                  ? 'bg-green-100 text-green-800'
                  : match.match_score >= 70
                  ? 'bg-blue-100 text-blue-800'
                  : 'bg-yellow-100 text-yellow-800'

              return (
                <div
                  key={match.id}
                  className="p-3 border rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <h4 className="font-medium">{job.title}</h4>
                      <p className="text-sm text-gray-600">{job.company}</p>
                    </div>
                    <Badge className={matchColor}>
                      {Math.round(match.match_score)}% match
                    </Badge>
                  </div>
                  <div className="flex items-center gap-4 text-xs text-gray-500 mt-2">
                    {job.location && (
                      <div className="flex items-center gap-1">
                        <MapPin className="h-3 w-3" />
                        {job.location}
                      </div>
                    )}
                    {job.salary_min && job.salary_max && (
                      <div className="flex items-center gap-1">
                        <DollarSign className="h-3 w-3" />
                        {job.salary_currency}{job.salary_min / 1000}k-{job.salary_max / 1000}k
                      </div>
                    )}
                    {job.job_type && (
                      <Badge variant="outline" className="text-xs">
                        {job.job_type}
                      </Badge>
                    )}
                  </div>
                  <div className="flex gap-2 mt-3">
                    <Button size="sm" asChild>
                      <Link href={`/dashboard/jobs/${job.id}`}>View</Link>
                    </Button>
                    <Button size="sm" variant="outline">
                      Quick Apply
                    </Button>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
