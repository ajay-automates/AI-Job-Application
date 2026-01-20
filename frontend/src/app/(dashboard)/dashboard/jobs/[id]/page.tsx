import { createClient } from '@/lib/supabase/server'
import { notFound } from 'next/navigation'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  MapPin,
  DollarSign,
  Briefcase,
  Calendar,
  ExternalLink,
  Building2,
} from 'lucide-react'
import { AutoApplyButton } from '@/components/jobs/AutoApplyButton'
import Link from 'next/link'

export default async function JobDetailsPage({
  params,
}: {
  params: { id: string }
}) {
  const supabase = await createClient()

  const {
    data: { user },
  } = await supabase.auth.getUser()

  if (!user) {
    return null
  }

  // Get job details
  const { data: job } = await supabase
    .from('jobs')
    .select('*')
    .eq('id', params.id)
    .single()

  if (!job) {
    notFound()
  }

  // Get match score for this user
  const { data: match } = await supabase
    .from('job_matches')
    .select('match_score, match_reasons, ai_analysis')
    .eq('user_id', user.id)
    .eq('job_id', params.id)
    .single()

  // Check if already applied
  const { data: application } = await supabase
    .from('applications')
    .select('id, status, applied_at')
    .eq('user_id', user.id)
    .eq('job_id', params.id)
    .single()

  const matchColor =
    match && match.match_score >= 85
      ? 'bg-green-100 text-green-800'
      : match && match.match_score >= 70
      ? 'bg-blue-100 text-blue-800'
      : match && match.match_score >= 50
      ? 'bg-yellow-100 text-yellow-800'
      : 'bg-gray-100 text-gray-800'

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <h1 className="text-3xl font-bold">{job.title}</h1>
            {match && (
              <Badge className={matchColor}>
                {Math.round(match.match_score)}% match
              </Badge>
            )}
            {application && (
              <Badge variant="outline" className="capitalize">
                {application.status}
              </Badge>
            )}
          </div>
          <div className="flex items-center gap-2 text-lg text-gray-700">
            <Building2 className="h-5 w-5" />
            <span>{job.company}</span>
          </div>
        </div>

        <div className="flex gap-2">
          {!application && (
            <AutoApplyButton
              jobId={job.id}
              jobUrl={job.url}
              jobTitle={job.title}
              company={job.company}
              size="lg"
            />
          )}
          <Button size="lg" variant="outline" asChild>
            <a href={job.url} target="_blank" rel="noopener noreferrer">
              <ExternalLink className="mr-2 h-4 w-4" />
              View Original
            </a>
          </Button>
        </div>
      </div>

      {/* Job Info Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {job.location && (
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-2">
                <MapPin className="h-5 w-5 text-gray-500" />
                <div>
                  <p className="text-sm text-gray-500">Location</p>
                  <p className="font-semibold">{job.location}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {job.salary_min && job.salary_max && (
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-2">
                <DollarSign className="h-5 w-5 text-gray-500" />
                <div>
                  <p className="text-sm text-gray-500">Salary Range</p>
                  <p className="font-semibold">
                    {job.salary_currency}
                    {job.salary_min / 1000}k-{job.salary_max / 1000}k
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {job.job_type && (
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-2">
                <Briefcase className="h-5 w-5 text-gray-500" />
                <div>
                  <p className="text-sm text-gray-500">Job Type</p>
                  <p className="font-semibold capitalize">{job.job_type}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {job.posted_date && (
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-2">
                <Calendar className="h-5 w-5 text-gray-500" />
                <div>
                  <p className="text-sm text-gray-500">Posted Date</p>
                  <p className="font-semibold">
                    {new Date(job.posted_date).toLocaleDateString()}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {job.remote_type && (
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-2">
                <Briefcase className="h-5 w-5 text-gray-500" />
                <div>
                  <p className="text-sm text-gray-500">Work Type</p>
                  <p className="font-semibold capitalize">{job.remote_type}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* AI Match Analysis */}
      {match && match.ai_analysis && (
        <Card>
          <CardHeader>
            <CardTitle>AI Match Analysis</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <h3 className="font-semibold mb-2">Why This Job Matches</h3>
              {match.match_reasons && match.match_reasons.length > 0 ? (
                <ul className="list-disc list-inside space-y-1">
                  {match.match_reasons.map((reason: string, index: number) => (
                    <li key={index} className="text-gray-700">
                      {reason}
                    </li>
                  ))}
                </ul>
              ) : null}
            </div>
            <div>
              <h3 className="font-semibold mb-2">Detailed Analysis</h3>
              <p className="text-gray-700 whitespace-pre-wrap">
                {match.ai_analysis}
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Job Description */}
      <Card>
        <CardHeader>
          <CardTitle>Job Description</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="prose max-w-none">
            <p className="whitespace-pre-wrap text-gray-700">
              {job.description || 'No description available'}
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Application Status */}
      {application && (
        <Card>
          <CardHeader>
            <CardTitle>Application Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-600">Status:</span>
                <Badge variant="outline" className="capitalize">
                  {application.status}
                </Badge>
              </div>
              {application.applied_at && (
                <div className="flex justify-between">
                  <span className="text-gray-600">Applied:</span>
                  <span className="font-semibold">
                    {new Date(application.applied_at).toLocaleDateString()}
                  </span>
                </div>
              )}
              <Button asChild className="w-full mt-4">
                <Link href="/dashboard/applications">View All Applications</Link>
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Back Button */}
      <div className="flex justify-start">
        <Button variant="outline" asChild>
          <Link href="/dashboard/jobs">← Back to Jobs</Link>
        </Button>
      </div>
    </div>
  )
}
