import { createClient } from '@/lib/supabase/server'
import { notFound } from 'next/navigation'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  Calendar,
  ExternalLink,
  MapPin,
  Building2,
  FileText,
  AlertCircle,
  CheckCircle,
  Clock,
} from 'lucide-react'
import Link from 'next/link'

const statusColors: Record<string, string> = {
  pending: 'bg-yellow-100 text-yellow-800',
  in_progress: 'bg-blue-100 text-blue-800',
  applied: 'bg-green-100 text-green-800',
  interview: 'bg-purple-100 text-purple-800',
  offer: 'bg-emerald-100 text-emerald-800',
  rejected: 'bg-red-100 text-red-800',
  withdrawn: 'bg-gray-100 text-gray-800',
}

const automationStatusColors: Record<string, string> = {
  queued: 'bg-gray-100 text-gray-800',
  extracting: 'bg-blue-100 text-blue-800',
  filling: 'bg-yellow-100 text-yellow-800',
  completed: 'bg-green-100 text-green-800',
  failed: 'bg-red-100 text-red-800',
}

export default async function ApplicationDetailsPage({
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

  // Get application details with job info
  const { data: application } = await supabase
    .from('applications')
    .select(`
      *,
      jobs (
        id,
        title,
        company,
        location,
        url,
        description,
        salary_min,
        salary_max,
        salary_currency,
        job_type
      )
    `)
    .eq('id', params.id)
    .eq('user_id', user.id)
    .single()

  if (!application) {
    notFound()
  }

  const job = application.jobs

  // Get automation logs
  const { data: logs } = await supabase
    .from('automation_logs')
    .select('*')
    .eq('application_id', params.id)
    .order('created_at', { ascending: false })
    .limit(20)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <h1 className="text-3xl font-bold">
              {job?.title || 'Unknown Job'}
            </h1>
            <Badge
              className={
                statusColors[application.status] || statusColors.pending
              }
            >
              {application.status}
            </Badge>
            {application.automation_enabled && (
              <Badge variant="outline">🤖 Auto</Badge>
            )}
          </div>
          <div className="flex items-center gap-2 text-lg text-gray-700">
            <Building2 className="h-5 w-5" />
            <span>{job?.company || 'Unknown Company'}</span>
          </div>
        </div>

        <div className="flex gap-2">
          {job?.url && (
            <Button size="lg" variant="outline" asChild>
              <a href={job.url} target="_blank" rel="noopener noreferrer">
                <ExternalLink className="mr-2 h-4 w-4" />
                View Original Job
              </a>
            </Button>
          )}
          <Button size="lg" variant="outline" asChild>
            <Link href="/dashboard/applications">← Back to Applications</Link>
          </Button>
        </div>
      </div>

      {/* Application Info Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-2">
              <Calendar className="h-5 w-5 text-gray-500" />
              <div>
                <p className="text-sm text-gray-500">Created</p>
                <p className="font-semibold">
                  {new Date(application.created_at).toLocaleDateString()}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {application.applied_at && (
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-2">
                <CheckCircle className="h-5 w-5 text-green-500" />
                <div>
                  <p className="text-sm text-gray-500">Applied</p>
                  <p className="font-semibold">
                    {new Date(application.applied_at).toLocaleDateString()}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {application.interview_date && (
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-2">
                <Calendar className="h-5 w-5 text-purple-500" />
                <div>
                  <p className="text-sm text-gray-500">Interview</p>
                  <p className="font-semibold">
                    {new Date(application.interview_date).toLocaleDateString()}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {job?.location && (
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
      </div>

      {/* Automation Status */}
      {application.automation_enabled && (
        <Card>
          <CardHeader>
            <CardTitle>Automation Status</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Status</p>
                <Badge
                  className={
                    automationStatusColors[
                      application.automation_status || 'queued'
                    ] || automationStatusColors.queued
                  }
                >
                  {application.automation_status || 'queued'}
                </Badge>
              </div>
              {application.automation_status === 'completed' && (
                <div className="flex items-center gap-2 text-green-600">
                  <CheckCircle className="h-5 w-5" />
                  <span className="font-medium">Automation Complete</span>
                </div>
              )}
              {application.automation_status === 'failed' && (
                <div className="flex items-center gap-2 text-red-600">
                  <AlertCircle className="h-5 w-5" />
                  <span className="font-medium">Automation Failed</span>
                </div>
              )}
              {['queued', 'extracting', 'filling'].includes(
                application.automation_status || ''
              ) && (
                <div className="flex items-center gap-2 text-blue-600">
                  <Clock className="h-5 w-5 animate-pulse" />
                  <span className="font-medium">In Progress...</span>
                </div>
              )}
            </div>

            {application.automation_error && (
              <div className="bg-red-50 border border-red-200 rounded-md p-4">
                <p className="text-sm font-semibold text-red-800 mb-2">
                  Error Details:
                </p>
                <p className="text-sm text-red-700 whitespace-pre-wrap">
                  {application.automation_error}
                </p>
              </div>
            )}

            {application.automation_status === 'queued' && (
              <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
                <p className="text-sm text-blue-800">
                  ⏳ Your application is queued. The browser will open shortly
                  to fill the form automatically.
                </p>
              </div>
            )}

            {application.automation_status === 'filling' && (
              <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4">
                <p className="text-sm text-yellow-800">
                  🔄 Browser is opening and form is being filled. Please wait...
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Automation Logs */}
      {logs && logs.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Automation Logs</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {logs.map((log: any) => (
                <div
                  key={log.id}
                  className="flex items-start gap-3 p-3 bg-gray-50 rounded-md"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-medium text-sm">{log.action}</span>
                      {log.success ? (
                        <CheckCircle className="h-4 w-4 text-green-600" />
                      ) : (
                        <AlertCircle className="h-4 w-4 text-red-600" />
                      )}
                    </div>
                    <p className="text-xs text-gray-500">
                      {new Date(log.created_at).toLocaleString()}
                    </p>
                    {log.error_message && (
                      <p className="text-sm text-red-600 mt-1">
                        {log.error_message}
                      </p>
                    )}
                    {log.metadata && (
                      <pre className="text-xs text-gray-600 mt-1 overflow-auto">
                        {JSON.stringify(log.metadata, null, 2)}
                      </pre>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Notes */}
      {application.notes && (
        <Card>
          <CardHeader>
            <CardTitle>Notes</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="whitespace-pre-wrap text-gray-700">
              {application.notes}
            </p>
          </CardContent>
        </Card>
      )}

      {/* Job Description */}
      {job?.description && (
        <Card>
          <CardHeader>
            <CardTitle>Job Description</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="prose max-w-none">
              <p className="whitespace-pre-wrap text-gray-700">
                {job.description}
              </p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
