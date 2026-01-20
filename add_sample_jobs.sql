-- Sample Jobs to Test Your Platform
-- Run this in Supabase SQL Editor to add test jobs

-- Software Engineer at Google
INSERT INTO jobs (title, company, url, description, location, salary_min, salary_max, salary_currency, job_type, remote_type, is_active, posted_date)
VALUES 
(
  'Senior Software Engineer',
  'Google',
  'https://careers.google.com/jobs/results/123456789/',
  'We are looking for a Senior Software Engineer to join our team. You will work on cutting-edge technology, collaborate with talented engineers, and build products used by billions. Requirements: 5+ years experience, strong in Python/Java, system design expertise.',
  'Mountain View, CA',
  150000,
  200000,
  'USD',
  'full-time',
  'hybrid',
  true,
  NOW()
),

-- Frontend Developer at Meta
(
  'Frontend Developer',
  'Meta',
  'https://www.metacareers.com/jobs/987654321/',
  'Join Meta as a Frontend Developer. Build beautiful, responsive web applications using React, TypeScript, and modern web technologies. Work with designers and backend engineers to create amazing user experiences. Requirements: React, TypeScript, 3+ years experience.',
  'Menlo Park, CA',
  130000,
  180000,
  'USD',
  'full-time',
  'hybrid',
  true,
  NOW()
),

-- Full Stack Engineer at Stripe
(
  'Full Stack Engineer',
  'Stripe',
  'https://stripe.com/jobs/listing/123',
  'Stripe is looking for Full Stack Engineers to build the future of online payments. Work across the stack with Ruby, JavaScript, React, and PostgreSQL. Help us build products that power millions of businesses worldwide. Requirements: Full stack experience, strong CS fundamentals.',
  'San Francisco, CA',
  140000,
  190000,
  'USD',
  'full-time',
  'remote',
  true,
  NOW()
),

-- Backend Engineer at Netflix
(
  'Backend Engineer',
  'Netflix',
  'https://jobs.netflix.com/jobs/456789',
  'Netflix is hiring Backend Engineers to work on our streaming infrastructure. Build scalable microservices, optimize performance, and handle millions of concurrent users. Work with Java, Python, and distributed systems. Requirements: Backend experience, system design, scalability expertise.',
  'Los Gatos, CA',
  160000,
  210000,
  'USD',
  'full-time',
  'hybrid',
  true,
  NOW()
),

-- DevOps Engineer at Amazon
(
  'DevOps Engineer',
  'Amazon',
  'https://www.amazon.jobs/en/jobs/654321',
  'Amazon Web Services is looking for DevOps Engineers. Build and maintain cloud infrastructure, automate deployments, and ensure reliability at scale. Work with AWS, Kubernetes, Terraform, and CI/CD pipelines. Requirements: 4+ years DevOps experience, strong AWS knowledge.',
  'Seattle, WA',
  135000,
  185000,
  'USD',
  'full-time',
  'onsite',
  true,
  NOW()
),

-- Product Manager at Airbnb
(
  'Product Manager',
  'Airbnb',
  'https://careers.airbnb.com/positions/321654/',
  'Airbnb is seeking a Product Manager to drive product strategy and execution. Work with engineers, designers, and data scientists to build features that delight our community. Requirements: 3+ years PM experience, strong analytical skills, user-centric mindset.',
  'San Francisco, CA',
  145000,
  195000,
  'USD',
  'full-time',
  'hybrid',
  true,
  NOW()
),

-- Data Scientist at Uber
(
  'Data Scientist',
  'Uber',
  'https://www.uber.com/careers/list/147258/',
  'Join Uber as a Data Scientist. Analyze data, build ML models, and drive business decisions with insights. Work with Python, SQL, machine learning frameworks, and big data tools. Requirements: Statistics background, Python/R, ML experience, business acumen.',
  'San Francisco, CA',
  140000,
  180000,
  'USD',
  'full-time',
  'hybrid',
  true,
  NOW()
),

-- Mobile Engineer at Spotify
(
  'iOS Engineer',
  'Spotify',
  'https://www.lifeatspotify.com/jobs/963852',
  'Spotify is hiring iOS Engineers to build the music streaming app loved by millions. Work with Swift, SwiftUI, and modern iOS technologies. Create smooth, delightful user experiences. Requirements: Swift, iOS development, 4+ years mobile experience.',
  'New York, NY',
  135000,
  175000,
  'USD',
  'full-time',
  'hybrid',
  true,
  NOW()
),

-- Security Engineer at Cloudflare
(
  'Security Engineer',
  'Cloudflare',
  'https://www.cloudflare.com/careers/jobs/753951/',
  'Cloudflare needs Security Engineers to protect the internet. Build security tools, investigate threats, and secure our infrastructure. Work with security protocols, threat detection, and incident response. Requirements: Security expertise, penetration testing, network security.',
  'Austin, TX',
  145000,
  190000,
  'USD',
  'full-time',
  'remote',
  true,
  NOW()
),

-- ML Engineer at OpenAI
(
  'Machine Learning Engineer',
  'OpenAI',
  'https://openai.com/careers/machine-learning-engineer',
  'OpenAI is looking for ML Engineers to advance artificial intelligence. Train large language models, optimize performance, and push the boundaries of AI capabilities. Work with PyTorch, distributed systems, and cutting-edge ML. Requirements: Strong ML background, PhD or equivalent experience.',
  'San Francisco, CA',
  180000,
  250000,
  'USD',
  'full-time',
  'hybrid',
  true,
  NOW()
);

-- Success message
SELECT 'Successfully added 10 sample jobs!' AS message;
SELECT COUNT(*) AS total_jobs FROM jobs WHERE is_active = true;
