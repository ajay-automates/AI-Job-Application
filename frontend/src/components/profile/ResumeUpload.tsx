'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { createClient } from '@/lib/supabase/client'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { toast } from 'sonner'
import { FileText, Upload, X } from 'lucide-react'

interface ResumeUploadProps {
  profile: any
  userId: string
}

export function ResumeUpload({ profile, userId }: ResumeUploadProps) {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [file, setFile] = useState<File | null>(null)
  const [resumeText, setResumeText] = useState(profile?.resume_text || '')

  const hasResume = profile?.resume_text || profile?.resume_url

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
    }
  }

  const handleUpload = async () => {
    if (!file && !resumeText) {
      toast.error('Please select a file or enter resume text')
      return
    }

    setLoading(true)

    try {
      const supabase = createClient()

      if (file) {
        // Read file content
        const reader = new FileReader()
        reader.onload = async (e) => {
          try {
            let content = e.target?.result as string
            
            // Clean content to avoid Unicode escape sequence issues
            // Replace problematic characters that might cause issues
            content = content.replace(/[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]/g, '')
            
            // For binary files (PDF, DOCX), just store the filename
            // We'll handle proper parsing later with a backend service
            if (file.type === 'application/pdf' || 
                file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document') {
              content = `Resume file: ${file.name}\nPlease paste your resume text below for now. PDF/DOCX parsing coming soon!`
            }

            // Update profile with file content
            const { error } = await supabase
              .from('profiles')
              .update({
                resume_text: content,
                resume_url: file.name,
              })
              .eq('id', userId)

            if (error) {
              toast.error(error.message)
              setLoading(false)
              return
            }

            toast.success('Resume uploaded successfully!')
            router.refresh()
            setFile(null)
            setLoading(false)

            // Trigger AI job matching in background
            try {
              const matchResponse = await fetch('/api/jobs/match-all', {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                },
                body: JSON.stringify({ max_jobs: 50 }),
              })

              if (matchResponse.ok) {
                toast.success('AI Matching Started! 🤖 Finding the best job matches...')
              }
            } catch (error) {
              console.error('Failed to trigger matching:', error)
              // Don't show error to user, matching is optional
            }
          } catch (err) {
            toast.error('Error reading file. Please paste resume text instead.')
            console.error(err)
            setLoading(false)
          }
        }

        reader.onerror = () => {
          toast.error('Error reading file. Please paste resume text instead.')
          setLoading(false)
        }

        // Read as text with UTF-8 encoding
        reader.readAsText(file, 'UTF-8')
      } else if (resumeText) {
        // Save resume text
        const { error } = await supabase
          .from('profiles')
          .update({ resume_text: resumeText })
          .eq('id', userId)

        if (error) {
          toast.error(error.message)
          return
        }

        toast.success('Resume text saved successfully!')
        router.refresh()

        // Trigger AI job matching in background
        try {
          const matchResponse = await fetch('/api/jobs/match-all', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ max_jobs: 50 }),
          })

          if (matchResponse.ok) {
            toast.success('AI Matching Started! 🤖 Finding the best job matches...')
          }
        } catch (error) {
          console.error('Failed to trigger matching:', error)
          // Don't show error to user, matching is optional
        }
      }
    } catch (error) {
      toast.error('Failed to upload resume')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete your resume?')) {
      return
    }

    setLoading(true)

    try {
      const supabase = createClient()
      const { error } = await supabase
        .from('profiles')
        .update({
          resume_text: null,
          resume_url: null,
        })
        .eq('id', userId)

      if (error) {
        toast.error(error.message)
        return
      }

      toast.success('Resume deleted successfully!')
      setResumeText('')
      router.refresh()
    } catch (error) {
      toast.error('Failed to delete resume')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      {hasResume && (
        <div className="p-4 bg-green-50 border border-green-200 rounded-lg flex items-center justify-between">
          <div className="flex items-center gap-2">
            <FileText className="h-5 w-5 text-green-600" />
            <div>
              <p className="font-medium text-green-900">Resume uploaded</p>
              <p className="text-sm text-green-700">
                {profile?.resume_url || 'Resume text saved'}
              </p>
            </div>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleDelete}
            disabled={loading}
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
      )}

      <div className="space-y-2">
        <Label htmlFor="resume-text">Paste Your Resume Text (Recommended)</Label>
        <Textarea
          id="resume-text"
          value={resumeText}
          onChange={(e) => setResumeText(e.target.value)}
          placeholder="Paste your resume content here...&#10;&#10;Include:&#10;- Your name and contact info&#10;- Work experience&#10;- Education&#10;- Skills&#10;- Any relevant information for job applications"
          rows={15}
          disabled={loading}
          className="font-mono text-sm"
        />
        <p className="text-sm text-gray-500">
          💡 Tip: Copy your resume from a Word doc or PDF and paste it here as plain text
        </p>
      </div>

      <div className="flex items-center gap-4">
        <Button onClick={handleUpload} disabled={loading || (!file && !resumeText)}>
          {loading ? (
            'Saving...'
          ) : (
            <>
              <Upload className="mr-2 h-4 w-4" />
              {hasResume ? 'Update Resume' : 'Save Resume'}
            </>
          )}
        </Button>
        
        {!hasResume && (
          <div className="text-sm text-gray-500">
            Or upload a TXT file:
            <Input
              type="file"
              accept=".txt"
              onChange={handleFileChange}
              disabled={loading}
              className="mt-2 max-w-xs"
            />
          </div>
        )}
      </div>
    </div>
  )
}
