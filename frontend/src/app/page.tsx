import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Briefcase, Zap, Target, BarChart } from 'lucide-react'

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <header className="border-b bg-white/50 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Briefcase className="h-8 w-8 text-blue-600" />
            <span className="text-xl font-bold">JobAutomate</span>
          </div>
          <div className="flex gap-4">
            <Button variant="ghost" asChild>
              <Link href="/login">Login</Link>
            </Button>
            <Button asChild>
              <Link href="/signup">Get Started</Link>
            </Button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20 text-center">
        <h1 className="text-5xl font-bold text-gray-900 mb-6">
          Automate Your Job Search
        </h1>
        <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
          AI-powered platform that finds jobs, matches them to your resume,
          and automatically fills out applications. Land your dream job faster.
        </p>
        <div className="flex gap-4 justify-center">
          <Button size="lg" asChild>
            <Link href="/signup">Start Free Trial</Link>
          </Button>
          <Button size="lg" variant="outline" asChild>
            <Link href="/dashboard">View Dashboard</Link>
          </Button>
        </div>
      </section>

      {/* Features */}
      <section className="container mx-auto px-4 py-16">
        <h2 className="text-3xl font-bold text-center mb-12">
          Why JobAutomate?
        </h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card>
            <CardContent className="pt-6">
              <div className="h-12 w-12 rounded-lg bg-blue-100 flex items-center justify-center mb-4">
                <Zap className="h-6 w-6 text-blue-600" />
              </div>
              <h3 className="font-semibold mb-2">Auto-Apply</h3>
              <p className="text-sm text-gray-600">
                Automatically extract and fill job application forms in seconds
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="h-12 w-12 rounded-lg bg-green-100 flex items-center justify-center mb-4">
                <Target className="h-6 w-6 text-green-600" />
              </div>
              <h3 className="font-semibold mb-2">AI Matching</h3>
              <p className="text-sm text-gray-600">
                Find jobs that match your skills with 85%+ accuracy using AI
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="h-12 w-12 rounded-lg bg-purple-100 flex items-center justify-center mb-4">
                <BarChart className="h-6 w-6 text-purple-600" />
              </div>
              <h3 className="font-semibold mb-2">Track Applications</h3>
              <p className="text-sm text-gray-600">
                Monitor all your applications, interviews, and offers in one place
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="h-12 w-12 rounded-lg bg-yellow-100 flex items-center justify-center mb-4">
                <Briefcase className="h-6 w-6 text-yellow-600" />
              </div>
              <h3 className="font-semibold mb-2">Job Discovery</h3>
              <p className="text-sm text-gray-600">
                Discover thousands of jobs from top companies automatically
              </p>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* CTA */}
      <section className="container mx-auto px-4 py-16 text-center">
        <Card className="max-w-2xl mx-auto">
          <CardContent className="pt-6">
            <h2 className="text-2xl font-bold mb-4">Ready to Get Started?</h2>
            <p className="text-gray-600 mb-6">
              Join thousands of job seekers who are landing interviews faster
            </p>
            <Button size="lg" asChild>
              <Link href="/signup">Create Free Account</Link>
            </Button>
          </CardContent>
        </Card>
      </section>

      {/* Footer */}
      <footer className="border-t bg-white/50 mt-16">
        <div className="container mx-auto px-4 py-8 text-center text-sm text-gray-600">
          © 2026 JobAutomate. All rights reserved.
        </div>
      </footer>
    </div>
  )
}
