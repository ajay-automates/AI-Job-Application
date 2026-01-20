'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import { Loader2, Sparkles } from 'lucide-react'
import { useToast } from '@/components/ui/use-toast'

interface AutoApplyButtonProps {
  jobId: string
  jobUrl: string
  jobTitle: string
  company: string
  variant?: 'default' | 'outline' | 'ghost'
  size?: 'default' | 'sm' | 'lg'
  className?: string
  onSuccess?: () => void
}

export function AutoApplyButton({
  jobId,
  jobUrl,
  jobTitle,
  company,
  variant = 'default',
  size = 'default',
  className,
  onSuccess,
}: AutoApplyButtonProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [isApplying, setIsApplying] = useState(false)
  const { toast } = useToast()

  const handleAutoApply = async () => {
    setIsApplying(true)

    try {
      const response = await fetch('/api/automation/apply', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          job_id: jobId,
          job_url: jobUrl,
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Failed to start auto-apply')
      }

      toast({
        title: 'Auto-Apply Started! 🚀',
        description: `Application automation started for ${jobTitle} at ${company}. The browser will open shortly to fill the form.`,
      })

      setIsOpen(false)
      onSuccess?.()
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
    <>
      <Button
        variant={variant}
        size={size}
        className={className}
        onClick={() => setIsOpen(true)}
        disabled={isApplying}
      >
        {isApplying ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Applying...
          </>
        ) : (
          <>
            <Sparkles className="mr-2 h-4 w-4" />
            Auto Apply
          </>
        )}
      </Button>

      <AlertDialog open={isOpen} onOpenChange={setIsOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Start Auto-Apply?</AlertDialogTitle>
            <AlertDialogDescription className="space-y-2">
              <p>
                This will automatically fill the application form for:
              </p>
              <div className="bg-gray-50 p-3 rounded-md">
                <p className="font-semibold">{jobTitle}</p>
                <p className="text-sm text-gray-600">{company}</p>
              </div>
              <p className="text-sm">
                A browser window will open and the form will be filled automatically
                using your profile information. You'll be able to review everything
                before submitting.
              </p>
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={isApplying}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleAutoApply}
              disabled={isApplying}
              className="bg-blue-600 hover:bg-blue-700"
            >
              {isApplying ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Starting...
                </>
              ) : (
                'Start Auto-Apply'
              )}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  )
}
