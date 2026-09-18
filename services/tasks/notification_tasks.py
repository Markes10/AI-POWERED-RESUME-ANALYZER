"""
Celery tasks for notifications and communications.
"""
import logging
from celery import shared_task
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
    name="services.tasks.notification_tasks.send_email"
)
def send_email(self, to: str, subject: str, body: str, template: str = None, context: Dict = None) -> Dict[str, Any]:
    """
    Send an email notification.
    
    Args:
        to: Recipient email
        subject: Email subject
        body: Email body (HTML or text)
        template: Optional template name
        context: Template context variables
    
    Returns:
        Dict with send status
    """
    # In production, integrate with SendGrid, Mailgun, SES, etc.
    # For now, log the email
    logger.info(f"Sending email to {to}: {subject}")
    
    # Mock implementation
    return {
        "status": "sent",
        "to": to,
        "subject": subject,
        "message_id": f"mock-{hash(to + subject)}"
    }


@shared_task(
    name="services.tasks.notification_tasks.send_resume_analysis_complete"
)
def send_resume_analysis_complete(user_id: int, resume_id: int, match_score: float = None) -> Dict[str, Any]:
    """
    Notify user that resume analysis is complete.
    
    Args:
        user_id: User to notify
        resume_id: Resume that was analyzed
        match_score: Optional match score
    
    Returns:
        Dict with notification status
    """
    from db.database import get_db
    from db.models import User
    
    db = next(get_db())
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user or not user.email:
        return {"status": "skipped", "reason": "User not found or no email"}
    
    subject = "Your Resume Analysis is Complete"
    body = f"""
    Hi {user.username},
    
    Your resume analysis has been completed.
    Resume ID: {resume_id}
    {f'Match Score: {match_score:.1%}' if match_score else ''}
    
    Log in to view the full report.
    """
    
    return send_email.delay(user.email, subject, body).get()


@shared_task(
    name="services.tasks.notification_tasks.send_batch_complete"
)
def send_batch_complete(user_id: int, total: int, successful: int, failed: int) -> Dict[str, Any]:
    """
    Notify user that batch processing is complete.
    """
    from db.database import get_db
    from db.models import User
    
    db = next(get_db())
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user or not user.email:
        return {"status": "skipped", "reason": "User not found or no email"}
    
    subject = "Batch Resume Processing Complete"
    body = f"""
    Hi {user.username},
    
    Your batch resume processing has finished:
    - Total: {total}
    - Successful: {successful}
    - Failed: {failed}
    
    Log in to review the results.
    """
    
    return send_email.delay(user.email, subject, body).get()


@shared_task(
    name="services.tasks.notification_tasks.send_high_risk_alert"
)
def send_high_risk_alert(employee_data: Dict[str, Any], manager_emails: List[str]) -> Dict[str, Any]:
    """
    Send alert for high turnover risk employee.
    
    Args:
        employee_data: Employee risk assessment data
        manager_emails: List of manager emails to notify
    """
    subject = f"High Turnover Risk Alert: {employee_data.get('name', 'Employee')}"
    body = f"""
    An employee has been flagged with high turnover risk:
    
    Name: {employee_data.get('name')}
    Risk Level: {employee_data.get('risk_level')}
    Risk Score: {employee_data.get('risk_score')}%
    Factors: {', '.join(employee_data.get('factors', []))}
    
    Recommended actions:
    - Schedule 1-on-1 meeting
    - Review compensation and growth opportunities
    - Address specific risk factors
    """
    
    results = []
    for email in manager_emails:
        result = send_email.delay(email, subject, body).get()
        results.append(result)
    
    return {"sent": len(results), "results": results}


@shared_task(
    name="services.tasks.notification_tasks.send_interview_reminder"
)
def send_interview_reminder(interview_id: int, reminder_type: str = "24h") -> Dict[str, Any]:
    """
    Send interview reminder to interviewer and candidate.
    """
    from db.database import get_db
    from db.models import Interview, User
    
    db = next(get_db())
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    
    if not interview:
        return {"status": "skipped", "reason": "Interview not found"}
    
    candidate = db.query(User).filter(User.id == interview.candidate_id).first()
    
    subject = f"Interview Reminder: {interview.job.title if interview.job else 'Interview'}"
    body = f"""
    Reminder: You have an interview scheduled.
    
    {f'Candidate: {candidate.username}' if candidate else ''}
    Date: {interview.interview_date}
    Type: {reminder_type} reminder
    """
    
    # Send to interviewers (would need interviewer relationships)
    return send_email.delay(candidate.email if candidate else "", subject, body).get()


@shared_task(
    name="services.tasks.notification_tasks.send_learning_recommendation"
)
def send_learning_recommendation(user_id: int, recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Send personalized learning recommendations.
    """
    from db.database import get_db
    from db.models import User
    
    db = next(get_db())
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user or not user.email:
        return {"status": "skipped", "reason": "User not found or no email"}
    
    subject = "Your Personalized Learning Recommendations"
    
    courses_html = ""
    for rec in recommendations[:5]:
        courses_html += f"""
        <li><strong>{rec.get('course', 'Course')}</strong> - {rec.get('provider', '')}
        <br><small>{rec.get('reason', '')}</small></li>
        """
    
    body = f"""
    Hi {user.username},
    
    Based on your profile and career goals, here are recommended learning paths:
    
    <ul>{courses_html}</ul>
    
    Log in to view the complete learning path.
    """
    
    return send_email.delay(user.email, subject, body).get()