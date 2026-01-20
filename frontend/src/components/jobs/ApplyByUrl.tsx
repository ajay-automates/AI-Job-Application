'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { Loader2, Link as LinkIcon, Sparkles } from 'lucide-react'
import { useToast } from '@/components/ui/use-toast'

export function ApplyByUrl() {
  const [isOpen, setIsOpen] = useState(false)
  const [isApplying, setIsApplying] = useState(false)
  const [jobUrl, setJobUrl] = useState('')
  const { toast } = useToast()

  const isValidUrl = (url: string) => {
    try {
      new URL(url)
      return true
    } catch {
      return false
    }
  }

  const handleApply = async () => {
    if (!jobUrl.trim()) {
      toast({
        title: 'URL Required',
        description: 'Please enter a job URL',
        variant: 'destructive',
      })
      return
    }

    if (!isValidUrl(jobUrl.trim())) {
      toast({
        title: 'Invalid URL',
        description: 'Please enter a valid job URL (e.g., https://...)',
        variant: 'destructive',
      })
      return
    }

    setIsApplying(true)

    try {
      const response = await fetch('/api/automation/apply', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          job_url: jobUrl.trim(),
          job_title: "Job from URL",
          company: "Unknown",
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Failed to start auto-apply')
      }

      toast({
        title: 'Auto-Apply Started! 🚀',
        description: `Application automation started for the job. The browser will open shortly to fill the form.`,
      })

      setIsOpen(false)
      setJobUrl('')
    } catch (error) {
      console.error('Auto-apply error:', error)
      toast({
        title: 'Auto-Apply Failed',
        description:
          error instanceof Error
            ? error.message
            : 'Failed to start auto-apply. Please try again.',
        variant: 'destructive',
      })
    } finally {
      setIsApplying(false)
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" className="gap-2">
          <LinkIcon className="h-4 w-4" />
          Apply by URL
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Apply to Job by URL</DialogTitle>
          <DialogDescription>
            Paste the job application URL directly. We'll automatically fill out
            the application form for you.
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="grid gap-2">
            <Label htmlFor="job-url">
              Job Application URL <span className="text-red-500">*</span>
            </Label>
            <Input
              id="job-url"
              placeholder="https://company.com/careers/job-123"
              value={jobUrl}
              onChange={(e) => setJobUrl(e.target.value)}
              disabled={isApplying}
              type="url"
            />
            <p className="text-xs text-gray-500">
              Paste the full URL of the job application page
            </p>
          </div>
        </div>
        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => setIsOpen(false)}
            disabled={isApplying}
          >
            Cancel
          </Button>
          <Button onClick={handleApply} disabled={isApplying}>
            {isApplying ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Applying...
              </>
            ) : (
              <>
                <Sparkles className="mr-2 h-4 w-4" />
                Start Auto-Apply
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
