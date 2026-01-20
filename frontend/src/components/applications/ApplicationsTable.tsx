'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { ExternalLink, Calendar } from 'lucide-react'

interface Application {
  id: string
  status: string
  applied_at: string | null
  created_at: string
  notes: string | null
  interview_date: string | null
  automation_enabled: boolean
  automation_status: string | null
  jobs: {
    id: string
    title: string
    company: string
    location: string | null
    url: string
  } | null
}

interface ApplicationsTableProps {
  applications: Application[]
}

const statusColors: Record<string, string> = {
  pending: 'bg-yellow-100 text-yellow-800',
  in_progress: 'bg-blue-100 text-blue-800',
  applied: 'bg-green-100 text-green-800',
  interview: 'bg-purple-100 text-purple-800',
  offer: 'bg-emerald-100 text-emerald-800',
  rejected: 'bg-red-100 text-red-800',
  withdrawn: 'bg-gray-100 text-gray-800',
}

export function ApplicationsTable({ applications }: ApplicationsTableProps) {
  const [filter, setFilter] = useState<string>('all')

  const filteredApplications =
    filter === 'all'
      ? applications
      : applications.filter((app) => app.status === filter)

  if (applications.length === 0) {
    return (
      <Card>
        <CardContent className="py-12 text-center text-gray-500">
          <p>No applications yet</p>
          <p className="text-sm mt-2">Start applying to jobs to see them here</p>
          <Button className="mt-4" asChild>
            <Link href="/dashboard/jobs">Browse Jobs</Link>
          </Button>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="font-semibold">
          {filteredApplications.length} Application(s)
        </h3>
        <Select value={filter} onValueChange={setFilter}>
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Filter by status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Statuses</SelectItem>
            <SelectItem value="pending">Pending</SelectItem>
            <SelectItem value="applied">Applied</SelectItem>
            <SelectItem value="interview">Interview</SelectItem>
            <SelectItem value="offer">Offer</SelectItem>
            <SelectItem value="rejected">Rejected</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-3">
        {filteredApplications.map((app) => (
          <Card key={app.id} className="hover:shadow-md transition-shadow">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h4 className="font-semibold">
                      {app.jobs?.title || 'Unknown Job'}
                    </h4>
                    <Badge className={statusColors[app.status] || statusColors.pending}>
                      {app.status}
                    </Badge>
                    {app.automation_enabled && (
                      <Badge variant="outline">🤖 Auto</Badge>
                    )}
                  </div>

                  <p className="text-sm text-gray-600">
                    {app.jobs?.company || 'Unknown Company'} •{' '}
                    {app.jobs?.location || 'Location not specified'}
                  </p>

                  <div className="flex items-center gap-4 text-xs text-gray-500 mt-2">
                    <span>
                      Created: {new Date(app.created_at).toLocaleDateString()}
                    </span>
                    {app.applied_at && (
                      <span>
                        Applied: {new Date(app.applied_at).toLocaleDateString()}
                      </span>
                    )}
                    {app.interview_date && (
                      <span className="flex items-center gap-1 text-purple-600 font-medium">
                        <Calendar className="h-3 w-3" />
                        Interview: {new Date(app.interview_date).toLocaleDateString()}
                      </span>
                    )}
                  </div>

                  {app.notes && (
                    <p className="text-sm text-gray-600 mt-2 italic">
                      "{app.notes.substring(0, 100)}
                      {app.notes.length > 100 ? '...' : ''}"
                    </p>
                  )}
                </div>

                <div className="flex flex-col gap-2">
                  <Button size="sm" variant="outline" asChild>
                    <Link href={`/dashboard/applications/${app.id}`}>
                      View
                    </Link>
                  </Button>
                  {app.jobs?.url && (
                    <Button size="sm" variant="ghost" asChild>
                      <a
                        href={app.jobs.url}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        <ExternalLink className="h-4 w-4" />
                      </a>
                    </Button>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
