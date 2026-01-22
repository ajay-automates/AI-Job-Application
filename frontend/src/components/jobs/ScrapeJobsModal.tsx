'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Loader2, Plus } from 'lucide-react'
import { useToast } from '@/components/ui/use-toast'
import { useRouter } from 'next/navigation'

export function ScrapeJobsModal() {
  const [isOpen, setIsOpen] = useState(false)
  const [isScraping, setIsScraping] = useState(false)
  const [keywords, setKeywords] = useState('')
  const [location, setLocation] = useState('')
  const { toast } = useToast()
  const router = useRouter()

  const handleScrape = async () => {
    if (!keywords.trim()) {
      toast({
        title: 'Keywords Required',
        description: 'Please enter keywords to search for jobs',
        variant: 'destructive',
      })
      return
    }

    setIsScraping(true)

    try {
      const response = await fetch('/api/automation/scrape', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          keywords: keywords.trim(),
          location: location.trim() || undefined,
          max_results: 50,
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Failed to scrape jobs')
      }

      toast({
        title: 'Job Scraping Started! 🎯',
        description: `Searching for jobs matching "${keywords}". This may take a minute...`,
      })

      setIsOpen(false)
      setKeywords('')
      setLocation('')

      // Refresh the page after a delay to show new jobs
      setTimeout(() => {
        router.refresh()
        toast({
          title: 'Jobs Updated!',
          description: 'New jobs have been added to your list.',
        })
      }, 3000)
    } catch (error) {
      console.error('Scrape error:', error)
      toast({
        title: 'Scraping Failed',
        description:
          error instanceof Error
            ? error.message
            : 'Failed to scrape jobs. Please try again.',
        variant: 'destructive',
      })
    } finally {
      setIsScraping(false)
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Scrape New Jobs
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Scrape New Jobs</DialogTitle>
          <DialogDescription>
            Search for jobs from multiple job boards. Enter keywords and optionally
            a location to find relevant positions.
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="grid gap-2">
            <Label htmlFor="keywords">
              Keywords <span className="text-red-500">*</span>
            </Label>
            <Input
              id="keywords"
              placeholder="e.g., Software Engineer, Data Analyst"
              value={keywords}
              onChange={(e) => setKeywords(e.target.value)}
              disabled={isScraping}
            />
            <p className="text-xs text-gray-500">
              Enter job titles, skills, or keywords
            </p>
          </div>
          <div className="grid gap-2">
            <Label htmlFor="location">Location (Optional)</Label>
            <Input
              id="location"
              placeholder="e.g., San Francisco, Remote"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              disabled={isScraping}
            />
            <p className="text-xs text-gray-500">
              Leave empty to search all locations
            </p>
          </div>
        </div>
        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => setIsOpen(false)}
            disabled={isScraping}
          >
            Cancel
          </Button>
          <Button onClick={handleScrape} disabled={isScraping}>
            {isScraping ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Scraping...
              </>
            ) : (
              'Start Scraping'
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
