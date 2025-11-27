# JobBuddy User Manual

Complete guide to using JobBuddy - Your Personal Job Search Assistant

## 📋 Table of Contents

1. [Getting Started](#getting-started)
2. [Accessing JobBuddy](#accessing-jobbuddy)
3. [Account Setup](#account-setup)
4. [Onboarding Process](#onboarding-process)
5. [Dashboard Overview](#dashboard-overview)
6. [Features Guide](#features-guide)
7. [Frequently Asked Questions (FAQ)](#frequently-asked-questions-faq)
8. [Troubleshooting](#troubleshooting)
9. [Business Rules & Best Practices](#business-rules--best-practices)
10. [Tips & Tricks](#tips--tricks)

---

## 🚀 Getting Started

### What is JobBuddy?

JobBuddy is a comprehensive job search tracking application designed to help you:
- Track all your job applications in one place
- Manage target companies and contacts
- Analyze your CV for ATS (Applicant Tracking System) compatibility
- Set and track weekly goals
- Build streaks to stay motivated
- Access curated resources and career coaches
- Get notifications for follow-ups and reminders

---

## 🌐 Accessing JobBuddy

### Option 1: Use the Live Application (Recommended)

**Live Application URL:** [https://jobbuddy-frontend.onrender.com](https://jobbuddy-frontend.onrender.com)

**Steps:**
1. Open your web browser (Chrome, Firefox, Safari, or Edge)
2. Navigate to: `https://jobbuddy-frontend.onrender.com`
3. Wait 30-60 seconds for the first load (free tier hosting)
4. Start using the application!

**Note:** The first request may take 30-60 seconds as the service wakes up from sleep. This is normal for free tier hosting. Subsequent requests will be much faster.

### Option 2: Run Locally on Your Computer

If you want to run JobBuddy on your computer, you'll need to:

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/VeronicahWanjuu/Job-buddy.git
   cd Job-buddy-1
   ```

2. **Set Up Backend:**
   ```bash
   cd backend
   python -m venv venv
   # Windows:
   .\venv\Scripts\Activate.ps1
   # Mac/Linux:
   source venv/bin/activate
   
   pip install -r requirements.txt
   python app.py
   ```

3. **Set Up Frontend (in a new terminal):**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **Access the Application:**
   - Open your browser
   - Go to: `http://localhost:5173`

For detailed setup instructions, see the [README.md](../README.md) file.

---

## 👤 Account Setup

### Creating an Account

1. **Navigate to the Registration Page:**
   - If using the live app: Go to [https://jobbuddy-frontend.onrender.com/register](https://jobbuddy-frontend.onrender.com/register)
   - If running locally: Go to `http://localhost:5173/register`

2. **Fill in Your Information:**
   - **Name:** Your full name
   - **Email:** A valid email address (this will be your login username)
   - **Password:** Choose a strong password (minimum 6 characters)

3. **Click "Register"**
   - You'll see a success message
   - You'll be automatically redirected to the onboarding process

### Logging In

1. **Navigate to the Login Page:**
   - If using the live app: Go to [https://jobbuddy-frontend.onrender.com/login](https://jobbuddy-frontend.onrender.com/login)
   - If running locally: Go to `http://localhost:5173/login`

2. **Enter Your Credentials:**
   - **Email:** The email you used to register
   - **Password:** Your account password

3. **Click "Login"**
   - You'll be redirected to your dashboard (if onboarding is complete)
   - Or to the onboarding process (if it's your first time)

### Forgot Password?

Currently, password reset functionality is not available. If you forget your password, you'll need to create a new account with a different email address.

---

## 🎯 Onboarding Process

When you first register, you'll go through a 7-step onboarding process to personalize your JobBuddy experience.

### Step 1: Welcome
- Introduction to JobBuddy
- Overview of what you'll be setting up

### Step 2: How You Feel
- Select your current job search status
- Options include: "Excited", "Nervous", "Confident", "Overwhelmed", etc.
- This helps personalize your experience

### Step 3: Dream Milestone
- Enter your dream job or career goal
- Example: "Software Engineer at Google" or "Marketing Manager"
- This will appear on your dashboard as motivation

### Step 4: Weekly Goals
- **Applications Goal:** How many applications you want to submit per week (default: 5)
- **Outreach Goal:** How many outreach messages you want to send per week (default: 3)
- You can adjust these later in your profile

### Step 5: Target Companies
- Add companies you're interested in working for
- Click "Add Company" to add each one
- You can add:
  - Company name
  - Industry
  - Location
  - Website
  - Notes
- You can skip this step and add companies later

### Step 6: Review
- Review all the information you've entered
- Make any changes if needed
- Click "Complete Onboarding" when ready

### Step 7: Celebration
- Congratulations! You're all set up
- You'll be automatically redirected to your dashboard

**Note:** You can always update your onboarding information later in your profile settings.

---

## 📊 Dashboard Overview

The dashboard is your command center. It shows:

### Welcome Widget
- Personalized greeting based on time of day
- Your dream milestone for motivation
- Located at the top of the dashboard

### Weekly Goals Widget
- **Applications Progress:** Shows how many applications you've submitted vs. your goal
- **Outreach Progress:** Shows how many outreach messages you've sent vs. your goal
- Visual progress bars
- Days remaining in the week

### Streak Widget
- **Current Streak:** Your consecutive days of job search activity
- **Best Streak:** Your longest streak ever
- **Level:** Your current level based on activity
- **Level Name:** Your achievement level (e.g., "Getting Started", "On Fire")

### Total Points Widget
- Your total accumulated points
- Points are earned by completing activities (applications, outreach, micro-quests)

### Micro-Quests Widget
- Daily tasks to help you stay productive
- Each quest has:
  - Title and description
  - Points you'll earn
  - A checkmark button to complete
- Complete quests to earn points and build your streak

### Recent Applications Widget
- Shows your 5 most recent job applications
- Quick view of:
  - Job title
  - Company name
  - Application date
  - Current status
- Click "View All" to see all applications

### Quick Actions Widget
- **Add Application:** Track a new job application
- **Add Company:** Add a target company to your list
- **Analyze CV:** Check your CV's ATS score

---

## 📚 Features Guide

### 1. Applications Management

#### Viewing Applications
- Navigate to **Applications** from the sidebar
- Applications are organized in a Kanban board with columns:
  - **Planned:** Applications you're planning to submit
  - **Applied:** Applications you've already submitted
  - **Interview:** Applications in the interview stage
  - **Offer:** Applications where you received an offer
  - **Rejected:** Applications that were rejected

#### Adding an Application
1. Click **"Add Application"** button (top right)
2. Fill in the form:
   - **Company:** Select from your saved companies or add a new one
   - **Job Title:** The position title
   - **Job URL:** (Optional) Link to the job posting
   - **Status:** Current status (default: Planned)
   - **Notes:** (Optional) Any additional information
3. Click **"Add Application"**

#### Updating Application Status
- **Drag and Drop:** Click and drag an application card to move it between columns
- The status will automatically update
- You'll see a success notification

#### Viewing Application Details
- Click on any application card
- View detailed information including:
  - Full application details
  - Notes
  - Outreach activities
  - CV analysis results (if any)

#### Editing/Deleting Applications
- Click the three dots (⋮) on an application card
- Select "Edit" or "Delete"
- Confirm deletion if prompted

### 2. Companies Management

#### Viewing Companies
- Navigate to **Companies** from the sidebar
- See all your target companies in a grid layout
- Filter by industry using the dropdown

#### Adding a Company
1. Click **"Add Company"** button
2. Fill in the form:
   - **Name:** Company name (required)
   - **Industry:** Select or type industry
   - **Location:** City, State/Country
   - **Website:** Company website URL
   - **Notes:** Any additional information
3. Click **"Add Company"**

#### Viewing Company Details
- Click **"View Details"** on any company card
- See:
  - Company information
  - All applications for this company
  - Contacts associated with this company

#### Editing/Deleting Companies
- Click the edit (✏️) or delete (🗑️) icons on a company card
- **Warning:** Deleting a company will also delete all related contacts and applications

### 3. Contacts Management

#### Adding Contacts
1. Go to a company's detail page
2. Click **"Add Contact"**
3. Fill in:
   - **Name:** Contact's full name
   - **Role/Title:** Their position
   - **Email:** Contact email
   - **LinkedIn URL:** (Optional) Their LinkedIn profile
   - **Notes:** Any additional information
4. Click **"Add Contact"**

#### Managing Contacts
- View all contacts on a company's detail page
- Edit or delete contacts using the icons
- Generate outreach messages for contacts

### 4. CV Analysis

#### Analyzing Your CV
1. Navigate to **CV Matcher** from the sidebar
2. Click the **"Analyze CV"** tab
3. Click **"Choose File"** and select your CV (PDF or DOCX)
4. Enter the job description (optional but recommended)
5. Click **"Analyze CV"**
6. Wait for the analysis to complete

#### Understanding Your ATS Score
- **70% and above:** Excellent - Your CV is well-optimized
- **50-69%:** Good - Some improvements needed
- **Below 50%:** Needs work - Review suggestions and update your CV

#### Viewing Analysis Results
- See your ATS score
- Review keyword matches
- Get suggestions for improvement
- View analysis history in the **"History"** tab

#### CV Analysis History
- View all past CV analyses
- Click on any analysis to see detailed results
- Compare scores over time

### 5. Goals & Streaks

#### Understanding Streaks
- A **streak** is consecutive days of job search activity
- Activities that count:
  - Adding an application
  - Sending an outreach message
  - Completing a micro-quest
  - Updating application status

#### Building Your Streak
- Complete at least one activity per day
- Your streak counter increases each day
- If you miss a day, your streak resets to 0
- Try to beat your best streak!

#### Weekly Goals
- Set goals for applications and outreach at the start of each week
- Track your progress on the dashboard
- Goals reset automatically each week
- Adjust goals in your profile settings

### 6. Micro-Quests

#### What are Micro-Quests?
- Small, daily tasks to keep you productive
- Examples:
  - "Submit 1 application today"
  - "Update your LinkedIn profile"
  - "Research 3 companies"
  - "Send 1 outreach message"

#### Completing Quests
1. View available quests on your dashboard
2. Read the quest description
3. Complete the task
4. Click the checkmark (✓) button
5. Earn points instantly!

#### Quest Benefits
- Earn points for each completed quest
- Points contribute to your total score
- Completing quests helps maintain your streak
- New quests appear daily

### 7. Outreach Management

#### Generating Outreach Messages
1. Go to a company's detail page
2. Find a contact
3. Click **"Generate Outreach"** button
4. Select the template type:
   - **Cold Outreach to Recruiter**
   - **Follow-up After Application**
   - **LinkedIn Connection Request**
   - **Thank You After Interview**
   - **Request for Informational Interview**
5. Review the generated message
6. Edit if needed
7. Click **"Log This Outreach"**

#### Logging Outreach Activities
- After generating a message, log it to track your outreach
- Fill in:
  - **Type:** Email, LinkedIn, Phone, etc.
  - **Subject:** Message subject
  - **Message:** The outreach content
  - **Date:** When you sent it
- This helps you track follow-ups

#### Viewing Outreach History
- See all outreach activities on a company's detail page
- Track when you last contacted someone
- Set reminders for follow-ups

### 8. Resources

#### Accessing Resources
- Navigate to **Resources** from the sidebar
- Browse curated learning resources
- Filter by category:
  - Interview preparation
  - Resume writing
  - Networking
  - Salary negotiation
  - Career development

#### Using Resources
- Click on any resource card
- Click **"View Resource"** to open the link
- Resources open in a new tab
- Bookmark useful resources for later

### 9. Career Coaches

#### Finding Coaches
- Navigate to **Coaches** from the sidebar
- Browse available career coaches
- See their:
  - Specialization
  - Hourly rate
  - Languages spoken
  - Availability status
  - Bio and experience

#### Contacting Coaches
- Click **"Email"** to send an email
- Click **"LinkedIn"** to view their LinkedIn profile
- Reach out to coaches directly through their preferred method

### 10. Notifications

#### Viewing Notifications
- Click the bell icon (🔔) in the top navigation bar
- See unread notification count (red badge)
- Navigate to **Notifications** page for full list

#### Notification Types
- **Follow-up Reminders:** Applications that need follow-up
- **Goal Progress:** Weekly goal updates
- **Streak Milestones:** Streak achievements
- **Quest Completions:** Points earned from quests
- **Application Updates:** Status changes

#### Managing Notifications
- **Mark as Read:** Click on a notification to mark it as read
- **Mark All Read:** Button to mark all notifications as read
- **Delete:** Remove individual notifications
- **Clear All:** Delete all notifications (cannot be undone)
- **Filter:** View all or only unread notifications

### 11. Profile Management

#### Accessing Your Profile
- Click your avatar/name in the top right
- Select **"Profile"** from the dropdown menu

#### Updating Profile Information
- Edit your name
- Update email (if supported)
- Change password (if supported)
- Update notification preferences
- Modify weekly goals

---

## ❓ Frequently Asked Questions (FAQ)

### General Questions

**Q: Is JobBuddy free to use?**  
A: Yes! JobBuddy is completely free to use. The live application is hosted on a free tier, which may have slower initial load times.

**Q: Do I need to create an account?**  
A: Yes, you need to create an account to use JobBuddy. This allows your data to be saved and synced across sessions.

**Q: Can I use JobBuddy on my phone?**  
A: Yes! JobBuddy is a web application that works on any device with a browser - desktop, tablet, or mobile phone.

**Q: Is my data secure?**  
A: Yes. Your data is stored securely, and your password is encrypted. However, always use a strong, unique password.

**Q: Can I export my data?**  
A: Currently, data export functionality is not available. This feature may be added in future updates.

### Account & Login

**Q: I forgot my password. How do I reset it?**  
A: Password reset functionality is currently not available. You'll need to create a new account with a different email address.

**Q: Can I change my email address?**  
A: Email change functionality may be available in your profile settings. If not, contact support.

**Q: Can I delete my account?**  
A: Account deletion functionality is currently not available. Contact support if you need to delete your account.

### Applications

**Q: How many applications can I track?**  
A: There's no limit! You can track as many applications as you need.

**Q: Can I add applications without a company?**  
A: No, you need to select or create a company first. This helps organize your applications better.

**Q: What happens if I delete an application?**  
A: The application will be permanently deleted. This action cannot be undone.

**Q: Can I edit an application after creating it?**  
A: Yes, click the three dots (⋮) on an application card and select "Edit". Note: Full edit functionality may be coming soon.

### CV Analysis

**Q: What file formats are supported for CV analysis?**  
A: PDF (.pdf) and Microsoft Word (.docx) files are supported.

**Q: What is an ATS score?**  
A: ATS (Applicant Tracking System) score measures how well your CV matches a job description. Higher scores (70%+) indicate better compatibility.

**Q: Is my CV stored securely?**  
A: Yes, your CV files are stored securely on the server. Only you can access your uploaded CVs.

**Q: Can I delete my CV files?**  
A: CV files are associated with analysis records. You can view your analysis history, but individual file deletion may not be available.

### Goals & Streaks

**Q: What happens if I miss a day?**  
A: Your streak will reset to 0. Don't worry - you can start building a new streak the next day!

**Q: How do I earn points?**  
A: You earn points by:
- Completing micro-quests
- Submitting applications
- Sending outreach messages
- Updating application statuses

**Q: Can I change my weekly goals?**  
A: Yes, you can update your weekly goals in your profile settings at any time.

**Q: Do goals reset automatically?**  
A: Yes, weekly goals reset every Monday. Your progress is tracked separately.

### Notifications

**Q: How often are notifications sent?**  
A: Notifications are generated automatically based on your activity and reminders. They appear in real-time.

**Q: Can I disable notifications?**  
A: You can manage notification preferences in your profile settings.

**Q: Do notifications expire?**  
A: Notifications don't expire, but you can delete them manually. They'll remain until you clear them.

### Technical Issues

**Q: The page is loading slowly. What should I do?**  
A: If using the live app, wait 30-60 seconds for the first load (free tier hosting). If it's still slow, try refreshing the page.

**Q: I'm getting an error message. What should I do?**  
A: Check the [Troubleshooting](#troubleshooting) section below. If the issue persists, try refreshing the page or clearing your browser cache.

**Q: Can I use JobBuddy offline?**  
A: No, JobBuddy requires an internet connection to function.

---

## 🔧 Troubleshooting

### Login Issues

**Problem: Can't log in**  
**Solutions:**
- Verify your email and password are correct
- Check for typos (email is case-sensitive)
- Try clearing your browser cache
- Make sure you're using the correct URL
- If using the live app, wait 30-60 seconds and try again

**Problem: "Invalid credentials" error**  
**Solutions:**
- Double-check your email and password
- Try resetting your password (if available)
- Make sure Caps Lock is not enabled
- Try logging in from a different browser

**Problem: Page keeps redirecting to login**  
**Solutions:**
- Clear your browser's localStorage
- Open browser console (F12) and run: `localStorage.clear()`
- Refresh the page
- Try logging in again

### Application Issues

**Problem: Can't add an application**  
**Solutions:**
- Make sure you've selected a company
- Check that all required fields are filled
- Verify your internet connection
- Try refreshing the page
- Check if the backend server is running (if running locally)

**Problem: Applications not showing**  
**Solutions:**
- Refresh the page
- Check your internet connection
- Make sure you're logged in
- Try logging out and logging back in
- Clear browser cache

**Problem: Can't drag and drop applications**  
**Solutions:**
- Make sure you're clicking and holding on the card
- Try refreshing the page
- Check your internet connection
- Try a different browser

### CV Analysis Issues

**Problem: Can't upload CV file**  
**Solutions:**
- Check file format (PDF or DOCX only)
- Verify file size is under 5MB
- Make sure the file is not corrupted
- Try a different file
- Check your internet connection

**Problem: Analysis taking too long**  
**Solutions:**
- Large files may take longer to process
- Wait a few minutes
- If it's been more than 5 minutes, try again
- Check your internet connection
- Try with a smaller file

**Problem: Analysis failed**  
**Solutions:**
- Make sure the file is a valid PDF or DOCX
- Check that the file is not password-protected
- Try a different file
- Make sure the file contains readable text (not just images)

### Dashboard Issues

**Problem: Dashboard not loading**  
**Solutions:**
- Wait 30-60 seconds (if using live app)
- Refresh the page
- Check your internet connection
- Clear browser cache
- Try logging out and logging back in

**Problem: Widgets showing incorrect data**  
**Solutions:**
- Refresh the page
- Wait a few seconds for data to load
- Check your internet connection
- Try logging out and logging back in

**Problem: Micro-Quests widget blinking/refreshing**  
**Solutions:**
- This should be fixed in the latest version
- Refresh the page
- Clear browser cache
- If it persists, contact support

### General Issues

**Problem: Page is white/blank**  
**Solutions:**
- Wait 30-60 seconds (if using live app)
- Refresh the page (Ctrl+F5 or Cmd+Shift+R)
- Clear browser cache
- Check browser console for errors (F12)
- Try a different browser
- Make sure JavaScript is enabled

**Problem: Buttons not working**  
**Solutions:**
- Refresh the page
- Clear browser cache
- Check your internet connection
- Try a different browser
- Make sure JavaScript is enabled

**Problem: Data not saving**  
**Solutions:**
- Check your internet connection
- Make sure you're logged in
- Wait a few seconds and try again
- Refresh the page
- Check browser console for errors (F12)

**Problem: Slow performance**  
**Solutions:**
- If using live app, this is normal for free tier (30-60 sec first load)
- Close other browser tabs
- Clear browser cache
- Try a different browser
- Check your internet connection speed

### Browser-Specific Issues

**Problem: Features not working in Safari**  
**Solutions:**
- Make sure you're using the latest version of Safari
- Enable JavaScript
- Clear Safari cache
- Try Chrome or Firefox

**Problem: Issues in Internet Explorer**  
**Solutions:**
- Internet Explorer is not supported
- Use Chrome, Firefox, Safari, or Edge instead

---

## 📋 Business Rules & Best Practices

### Application Tracking Rules

1. **One Application Per Job Posting**
   - Create a separate application for each unique job posting
   - Even if it's the same company, different positions should be separate applications

2. **Status Progression**
   - Applications typically progress: Planned → Applied → Interview → Offer/Rejected
   - You can move applications between any statuses as needed

3. **Company Requirement**
   - All applications must be associated with a company
   - This helps organize and track your applications better

### Goal Setting Rules

1. **Weekly Goals Reset**
   - Goals reset every Monday at midnight
   - Your progress is tracked separately from your goals
   - You can adjust goals anytime in your profile

2. **Realistic Goal Setting**
   - Set achievable goals based on your schedule
   - Start small and increase gradually
   - Quality over quantity - focus on well-targeted applications

### Streak Rules

1. **Daily Activity Requirement**
   - Complete at least one activity per day to maintain your streak
   - Activities include: adding applications, sending outreach, completing quests

2. **Streak Reset**
   - If you miss a day, your streak resets to 0
   - Your best streak is always saved
   - Start fresh and build a new streak!

3. **Points System**
   - Points are earned for various activities
   - Points contribute to your total score
   - Higher scores unlock achievements and levels

### Data Management Rules

1. **Data Ownership**
   - All your data belongs to you
   - You can delete applications, companies, and contacts at any time
   - Be careful - deletions cannot be undone

2. **Data Privacy**
   - Your data is stored securely
   - Only you can access your account
   - Use a strong, unique password

3. **Backup Recommendations**
   - Regularly review your applications
   - Export important information manually if needed
   - Keep track of important contacts outside the app as well

### Best Practices

1. **Regular Updates**
   - Update application statuses promptly
   - Log outreach activities immediately
   - Complete micro-quests daily

2. **Organization**
   - Keep company information up to date
   - Add notes to applications for context
   - Use consistent naming conventions

3. **Goal Achievement**
   - Set realistic weekly goals
   - Track your progress regularly
   - Celebrate milestones!

4. **CV Optimization**
   - Analyze your CV for each job application
   - Update your CV based on analysis suggestions
   - Keep multiple versions for different job types

5. **Networking**
   - Log all outreach activities
   - Follow up on applications after 1-2 weeks
   - Build relationships with contacts

---

## 💡 Tips & Tricks

### Productivity Tips

1. **Start Your Day Right**
   - Check your dashboard first thing in the morning
   - Review your goals for the week
   - Complete a micro-quest to start your day productively

2. **Batch Processing**
   - Add multiple applications at once
   - Update all application statuses together
   - Plan your week's outreach in advance

3. **Use Quick Actions**
   - The Quick Actions widget on your dashboard provides fast access to common tasks
   - Use it to quickly add applications, companies, or analyze your CV

4. **Set Reminders**
   - Use the notifications system to track follow-ups
   - Set personal reminders for important dates
   - Review notifications daily

### Organization Tips

1. **Company Management**
   - Add all target companies upfront
   - Organize by industry using the filter
   - Keep company information complete and up to date

2. **Application Tracking**
   - Use notes to record important details
   - Add job URLs for easy reference
   - Update statuses immediately after interviews or responses

3. **Contact Management**
   - Add contacts as you discover them
   - Link contacts to specific applications
   - Use outreach templates for consistency

### Motivation Tips

1. **Build Your Streak**
   - Complete at least one activity daily
   - Use micro-quests to maintain your streak
   - Celebrate streak milestones!

2. **Track Progress**
   - Review your dashboard regularly
   - Watch your points and level increase
   - See your weekly goal progress

3. **Stay Consistent**
   - Set a daily routine
   - Use JobBuddy at the same time each day
   - Make job searching a habit

### CV Optimization Tips

1. **Regular Analysis**
   - Analyze your CV for each job application
   - Compare scores over time
   - Update your CV based on suggestions

2. **Keyword Matching**
   - Use job descriptions to identify keywords
   - Incorporate relevant keywords into your CV
   - Re-analyze after making changes

3. **Multiple Versions**
   - Keep different CV versions for different industries
   - Tailor your CV for each application
   - Track which versions perform best

### Networking Tips

1. **Outreach Templates**
   - Use the outreach generator for consistency
   - Personalize templates for each contact
   - Follow up appropriately

2. **Contact Management**
   - Keep contact information organized
   - Log all interactions
   - Build relationships over time

3. **Follow-Up Strategy**
   - Follow up on applications after 1-2 weeks
   - Send thank-you notes after interviews
   - Stay in touch with contacts

---

## 🆘 Getting Help

### Support Resources

1. **Documentation**
   - Check this user manual first
   - Review the README.md file
   - Check backend and frontend README files

2. **GitHub Repository**
   - Visit: [https://github.com/VeronicahWanjuu/Job-buddy](https://github.com/VeronicahWanjuu/Job-buddy)
   - Check for known issues
   - Review the code if you're a developer

3. **Troubleshooting**
   - Review the [Troubleshooting](#troubleshooting) section above
   - Check browser console for errors (F12)
   - Try common solutions first

### Reporting Issues

If you encounter a bug or issue:
1. Check if it's a known issue
2. Try the troubleshooting steps
3. Note the steps to reproduce the issue
4. Check browser console for error messages
5. Report the issue on GitHub (if applicable)

---

## 📝 Quick Reference

### Keyboard Shortcuts
- **F5 / Ctrl+R:** Refresh page
- **Ctrl+F5 / Cmd+Shift+R:** Hard refresh (clear cache)
- **F12:** Open browser developer console
- **Esc:** Close modals/dialogs

### Important URLs
- **Live Application:** [https://jobbuddy-frontend.onrender.com](https://jobbuddy-frontend.onrender.com)
- **GitHub Repository:** [https://github.com/VeronicahWanjuu/Job-buddy](https://github.com/VeronicahWanjuu/Job-buddy)

### File Size Limits
- **CV Upload:** Maximum 5MB
- **Supported Formats:** PDF (.pdf), Microsoft Word (.docx)

### Browser Compatibility
- **Recommended:** Chrome, Firefox, Safari, Edge (latest versions)
- **Not Supported:** Internet Explorer

---

## 🎉 Conclusion

Congratulations! You now have everything you need to use JobBuddy effectively. Remember:

- **Consistency is key** - Use JobBuddy daily to build your streak
- **Stay organized** - Keep your applications and companies up to date
- **Track your progress** - Monitor your goals and celebrate achievements
- **Optimize your CV** - Use the CV analyzer to improve your applications
- **Network effectively** - Use outreach templates and track your contacts

**Happy job hunting! 🚀**

---

**Last Updated:** December 2024  
**Version:** 1.0  
**For technical documentation, see:** [README.md](../README.md)

