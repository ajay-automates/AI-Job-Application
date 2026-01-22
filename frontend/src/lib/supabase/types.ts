/**
 * Database Types
 * Generated from Supabase schema
 * Run: npx supabase gen types typescript --project-id YOUR_PROJECT_ID > src/lib/supabase/types.ts
 */

export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export interface Database {
  public: {
    Tables: {
      profiles: {
        Row: {
          id: string
          email: string
          full_name: string | null
          resume_text: string | null
          resume_url: string | null
          phone: string | null
          location: string | null
          preferences: Json
          created_at: string
          updated_at: string
        }
        Insert: {
          id: string
          email: string
          full_name?: string | null
          resume_text?: string | null
          resume_url?: string | null
          phone?: string | null
          location?: string | null
          preferences?: Json
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          email?: string
          full_name?: string | null
          resume_text?: string | null
          resume_url?: string | null
          phone?: string | null
          location?: string | null
          preferences?: Json
          created_at?: string
          updated_at?: string
        }
      }
      jobs: {
        Row: {
          id: string
          title: string
          company: string
          url: string
          description: string | null
          location: string | null
          salary_min: number | null
          salary_max: number | null
          salary_currency: string
          job_type: string | null
          remote_type: string | null
          posted_date: string | null
          expires_date: string | null
          source: string | null
          raw_data: Json | null
          scraped_at: string
          is_active: boolean
          created_at: string
        }
        Insert: {
          id?: string
          title: string
          company: string
          url: string
          description?: string | null
          location?: string | null
          salary_min?: number | null
          salary_max?: number | null
          salary_currency?: string
          job_type?: string | null
          remote_type?: string | null
          posted_date?: string | null
          expires_date?: string | null
          source?: string | null
          raw_data?: Json | null
          scraped_at?: string
          is_active?: boolean
          created_at?: string
        }
        Update: {
          id?: string
          title?: string
          company?: string
          url?: string
          description?: string | null
          location?: string | null
          salary_min?: number | null
          salary_max?: number | null
          salary_currency?: string
          job_type?: string | null
          remote_type?: string | null
          posted_date?: string | null
          expires_date?: string | null
          source?: string | null
          raw_data?: Json | null
          scraped_at?: string
          is_active?: boolean
          created_at?: string
        }
      }
      applications: {
        Row: {
          id: string
          user_id: string
          job_id: string | null
          status: string
          applied_at: string | null
          form_data: Json | null
          cover_letter: string | null
          notes: string | null
          interview_date: string | null
          follow_up_date: string | null
          automation_enabled: boolean
          automation_status: string | null
          automation_error: string | null
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          user_id: string
          job_id?: string | null
          status?: string
          applied_at?: string | null
          form_data?: Json | null
          cover_letter?: string | null
          notes?: string | null
          interview_date?: string | null
          follow_up_date?: string | null
          automation_enabled?: boolean
          automation_status?: string | null
          automation_error?: string | null
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          user_id?: string
          job_id?: string | null
          status?: string
          applied_at?: string | null
          form_data?: Json | null
          cover_letter?: string | null
          notes?: string | null
          interview_date?: string | null
          follow_up_date?: string | null
          automation_enabled?: boolean
          automation_status?: string | null
          automation_error?: string | null
          created_at?: string
          updated_at?: string
        }
      }
      job_matches: {
        Row: {
          id: string
          user_id: string
          job_id: string
          match_score: number
          match_reasons: Json | null
          ai_analysis: string | null
          is_favorited: boolean
          created_at: string
        }
        Insert: {
          id?: string
          user_id: string
          job_id: string
          match_score: number
          match_reasons?: Json | null
          ai_analysis?: string | null
          is_favorited?: boolean
          created_at?: string
        }
        Update: {
          id?: string
          user_id?: string
          job_id?: string
          match_score?: number
          match_reasons?: Json | null
          ai_analysis?: string | null
          is_favorited?: boolean
          created_at?: string
        }
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      [_ in never]: never
    }
    Enums: {
      [_ in never]: never
    }
  }
}
