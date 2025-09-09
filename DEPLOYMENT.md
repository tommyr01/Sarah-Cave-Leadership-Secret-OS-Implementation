# Sarah Cave Leadership OS - Deployment Guide

## GitHub + Vercel Deployment Setup

### Prerequisites
- GitHub account with access to: https://github.com/tommyr01/Sarah-Cave-Leadership-Secret-OS-Implementation
- Vercel account (can sign up with GitHub)
- OpenAI API key
- Airtable API key and base ID

### 1. Push Code to GitHub

```bash
cd "/Users/tommyrichardson/Cursor/Automation Developments/Sarah Cave OS/agents/sarah_cave_leadership_os"

# Initialize git if not already done
git init

# Add GitHub remote
git remote add origin https://github.com/tommyr01/Sarah-Cave-Leadership-Secret-OS-Implementation.git

# Add all files
git add .

# Commit
git commit -m "Initial Sarah Cave Leadership OS deployment setup

🤖 Generated with Claude Code

Co-Authored-By: Claude <noreply@anthropic.com>"

# Push to GitHub
git push -u origin main
```

### 2. Connect Vercel to GitHub

1. Go to [vercel.com](https://vercel.com) and sign in with GitHub
2. Click "New Project"
3. Import from Git: Select `tommyr01/Sarah-Cave-Leadership-Secret-OS-Implementation`
4. Configure project:
   - **Framework Preset**: Other
   - **Root Directory**: `./` (default)
   - **Build Command**: (leave empty)
   - **Output Directory**: (leave empty)

### 3. Set Environment Variables in Vercel

In Vercel dashboard → Project Settings → Environment Variables, add:

```
OPENAI_API_KEY=sk-your-openai-api-key-here
AIRTABLE_API_KEY=pat.your-airtable-personal-access-token
AIRTABLE_BASE_ID=appovmJ15ALIjbpDp
```

### 4. Deploy

Click "Deploy" in Vercel. Your endpoints will be available at:

- `https://your-project.vercel.app/api/webhook` - Main webhook router
- `https://your-project.vercel.app/api/lead_scoring` - Lead scoring automation
- `https://your-project.vercel.app/api/session_processing` - Session notes processing
- `https://your-project.vercel.app/api/client_health` - Client health monitoring  
- `https://your-project.vercel.app/api/business_intelligence` - BI reports
- `https://your-project.vercel.app/api/health` - System health check

### 5. Configure Airtable Webhooks

In Airtable, go to your base → Extensions → Webhooks:

1. **Leads Webhook**:
   - URL: `https://your-project.vercel.app/api/webhook/leads`
   - Tables: `Leads`
   - Events: `Record created`, `Record updated`

2. **Sessions Webhook**:
   - URL: `https://your-project.vercel.app/api/webhook/sessions`
   - Tables: `Coaching Sessions`
   - Events: `Record created`, `Record updated`

3. **Clients Webhook**:
   - URL: `https://your-project.vercel.app/api/webhook/clients`
   - Tables: `Clients`
   - Events: `Record updated`

### 6. Test Deployment

1. **Health Check**: Visit `https://your-project.vercel.app/api/health`
2. **Test Lead Scoring**: Create a test lead in Airtable
3. **Test Session Processing**: Add raw notes to a coaching session
4. **Monitor**: Check Vercel Functions logs for any errors

## Updating Code

To update the deployment:

```bash
# Make code changes locally
git add .
git commit -m "Update: description of changes"
git push

# Vercel automatically redeploys on push to main branch
```

## Monitoring

- **Vercel Dashboard**: View function logs and performance
- **Health Endpoints**: Monitor `/api/health` for system status
- **Airtable**: Verify webhook data is being processed correctly

## Troubleshooting

### Common Issues:

1. **Environment Variables Not Set**:
   - Check Vercel project settings
   - Redeploy after adding variables

2. **Import Errors**:
   - Verify `requirements.txt` has all dependencies
   - Check Python paths in API files

3. **Webhook Not Triggering**:
   - Verify webhook URLs in Airtable
   - Check webhook payload format
   - Review Vercel function logs

4. **AI Processing Failures**:
   - Verify OpenAI API key is valid
   - Check API usage limits
   - Review error logs for specific failures

## Production Checklist

- [ ] All environment variables configured
- [ ] Webhooks tested and working
- [ ] Health checks passing
- [ ] Error monitoring set up
- [ ] Sarah trained on the system
- [ ] Backup procedures documented
- [ ] Performance monitoring active