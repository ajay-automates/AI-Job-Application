import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@/lib/supabase/server'

export async function POST(request: NextRequest) {
  try {
    const supabase = await createClient()
    
    // Check authentication
    const {
      data: { user },
    } = await supabase.auth.getUser()

    if (!user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const body = await request.json()
    const { job_url, job_id, resume_url, cover_letter } = body

    if (!job_url) {
      return NextResponse.json(
        { error: 'Job URL is required' },
        { status: 400 }
      )
    }

    // Get user profile
    const { data: profile } = await supabase
      .from('profiles')
      .select('*')
      .eq('id', user.id)
      .single()

    if (!profile || !profile.resume_text) {
      return NextResponse.json(
        { error: 'Resume required. Please upload your resume first.' },
        { status: 400 }
      )
    }

    // Forward to backend
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    const response = await fetch(`${backendUrl}/api/automation/apply`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: user.id,
        job_url,
        resume_url,
        cover_letter,
      }),
    })

    if (!response.ok) {
      let errorMessage = 'Failed to start auto-apply'
      try {
        const error = await response.json()
        errorMessage = error.detail || error.message || error.error || errorMessage
      } catch {
        errorMessage = `Backend returned ${response.status}: ${response.statusText}`
      }
      return NextResponse.json(
        { error: errorMessage },
        { status: response.status }
      )
    }

    const data = await response.json()
    
    // Also create a link between job and application if job_id provided
    if (job_id && data.application_id) {
      await supabase
        .from('applications')
        .update({ job_id })
        .eq('id', data.application_id)
    }

    return NextResponse.json(data)
  } catch (error) {
    console.error('Auto-apply API error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
