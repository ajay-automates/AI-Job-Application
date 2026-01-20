'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { MapPin, DollarSign, Briefcase, ExternalLink } from 'lucide-react'

interface Job {
  id: string
  title: string
  company: string
  location: string | null
  salary_min: number | null
  salary_max: number | null
  salary_currency: string
  job_type: string | null
  remote_type: string | null
  url: string
  posted_date: string | null
}

interface JobsTableProps {
  jobs: Job[]
  matchScores: { [key: string]: number }
}

export function JobsTable({ jobs, matchScores }: JobsTableProps) {
  if (jobs.length === 0) {
    return (
      <Card>
        <CardContent className="py-12 text-center text-gray-500">
          <p>No jobs found</p>
          <p className="text-sm mt-2">Try adjusting your filters or scrape new jobs</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-4">
      {jobs.map((job) => {
        const matchScore = matchScores[job.id]
        const matchColor =
          matchScore >= 85
            ? 'bg-green-100 text-green-800'
            : matchScore >= 70
            ? 'bg-blue-100 text-blue-800'
            : matchScore >= 50
            ? 'bg-yellow-100 text-yellow-800'
            : 'bg-gray-100 text-gray-800'

        return (
          <Card key={job.id} className="hover:shadow-md transition-shadow">
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-xl font-semibold">{job.title}</h3>
                    {matchScore && (
                      <Badge className={matchColor}>
                        {Math.round(matchScore)}% match
                      </Badge>
                    )}
                  </div>

                  <p className="text-lg text-gray-700 mb-3">{job.company}</p>

                  <div className="flex flex-wrap gap-4 text-sm text-gray-600">
                    {job.location && (
                      <div className="flex items-center gap-1">
                        <MapPin className="h-4 w-4" />
                        {job.location}
                      </div>
                    )}

                    {job.salary_min && job.salary_max && (
                      <div className="flex items-center gap-1">
                        <DollarSign className="h-4 w-4" />
                        {job.salary_currency}
                        {job.salary_min / 1000}k-{job.salary_max / 1000}k
                      </div>
                    )}

                    {job.job_type && (
                      <div className="flex items-center gap-1">
                        <Briefcase className="h-4 w-4" />
                        {job.job_type}
                      </div>
                    )}

                    {job.remote_type && (
                      <Badge variant="outline">{job.remote_type}</Badge>
                    )}
                  </div>

                  {job.posted_date && (
                    <p className="text-xs text-gray-500 mt-2">
                      Posted {new Date(job.posted_date).toLocaleDateString()}
                    </p>
                  )}
                </div>

                <div className="flex flex-col gap-2">
                  <Button asChild size="sm">
                    <Link href={`/dashboard/jobs/${job.id}`}>View Details</Link>
                  </Button>
                  <Button size="sm" variant="outline" asChild>
                    <a href={job.url} target="_blank" rel="noopener noreferrer">
                      <ExternalLink className="mr-2 h-4 w-4" />
                      Original
                    </a>
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        )
      })}
    </div>
  )
}
