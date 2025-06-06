# 🚀 Deployment Guide

## Backend Deployment (Railway)

### Current Deployment
- **URL:** https://company-production-613d.up.railway.app/
- **Status:** ✅ Live and Running
- **Database:** MySQL on Railway

### Environment Variables
```env
DATABASE_URL=mysql+pymysql://root:password@mysql.railway.internal:3306/railway
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
FLASK_ENV=production
CORS_ORIGINS=*
PORT=5000
```

### Deployment Steps

1. **Connect GitHub Repository**
   - Link your GitHub repository to Railway
   - Select the `backend` directory as root

2. **Configure Environment Variables**
   - Add all required environment variables
   - Ensure DATABASE_URL points to Railway MySQL

3. **Deploy**
   - Railway automatically deploys on git push
   - Monitor deployment logs for any issues

### Database Setup

1. **Create MySQL Service**
   - Add MySQL service to your Railway project
   - Note the connection details

2. **Import Database Schema**
   - Use MySQL Workbench or Railway CLI
   - Import your SQL schema and data

3. **Update Connection String**
   - Use Railway's internal MySQL URL
   - Format: `mysql+pymysql://user:pass@host:port/db`

## Frontend Deployment (Coming Soon)

### Recommended Platforms
- **Vercel** (Recommended for React)
- **Netlify** (Alternative option)
- **Railway** (Full-stack option)

### Environment Variables for Frontend
```env
REACT_APP_API_URL=https://company-production-613d.up.railway.app
REACT_APP_ENV=production
```

### Deployment Steps (Vercel)

1. **Connect Repository**
   ```bash
   # Install Vercel CLI
   npm i -g vercel
   
   # Deploy
   vercel --prod
   ```

2. **Configure Build Settings**
   - Build Command: `npm run build`
   - Output Directory: `build`
   - Install Command: `npm install`

3. **Environment Variables**
   - Add environment variables in Vercel dashboard
   - Ensure API URL points to Railway backend

## Local Development

### Backend Setup
```bash
# Clone repository
git clone https://github.com/zmsaddi/Company.git
cd Company/backend

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="mysql+pymysql://user:pass@localhost:3306/company"
export SECRET_KEY="your-secret-key"
export JWT_SECRET_KEY="your-jwt-secret-key"

# Run application
python src/main.py
```

### Frontend Setup (Coming Soon)
```bash
# Navigate to frontend directory
cd Company/frontend

# Install dependencies
npm install

# Set environment variables
echo "REACT_APP_API_URL=http://localhost:5000" > .env

# Start development server
npm start
```

## Database Migration

### From Local to Railway

1. **Export Local Database**
   ```bash
   mysqldump -u username -p database_name > backup.sql
   ```

2. **Import to Railway**
   - Use MySQL Workbench
   - Connect to Railway MySQL
   - Import the SQL file

### Schema Updates
```bash
# Connect to Railway MySQL
mysql -h host -u user -p database

# Run migration scripts
source migration.sql
```

## Monitoring & Maintenance

### Railway Monitoring
- Check deployment logs regularly
- Monitor resource usage
- Set up alerts for downtime

### Database Backup
- Railway provides automatic backups
- Consider additional backup strategies
- Test restore procedures regularly

### Performance Optimization
- Monitor API response times
- Optimize database queries
- Use caching where appropriate

## Security Considerations

### Environment Variables
- Never commit secrets to git
- Use Railway's environment variable management
- Rotate secrets regularly

### Database Security
- Use strong passwords
- Limit database access
- Enable SSL connections

### API Security
- Implement rate limiting
- Use HTTPS only
- Validate all inputs
- Keep dependencies updated

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Check DATABASE_URL format
   - Verify MySQL service is running
   - Check network connectivity

2. **Deployment Failures**
   - Review build logs
   - Check requirements.txt
   - Verify Python version compatibility

3. **Environment Variable Issues**
   - Ensure all required variables are set
   - Check variable names and values
   - Restart service after changes

### Debug Commands
```bash
# Check Railway logs
railway logs

# Connect to Railway shell
railway shell

# Check environment variables
railway variables
```

## Scaling

### Horizontal Scaling
- Railway supports automatic scaling
- Monitor resource usage
- Consider load balancing for high traffic

### Database Scaling
- Monitor database performance
- Consider read replicas for heavy read workloads
- Optimize queries and indexes

---

*Last updated: June 6, 2025*

