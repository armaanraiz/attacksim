from flask import Blueprint, request, redirect, url_for, send_file, Response
from app.utils.email_sender import EmailTracker
import io
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('tracking', __name__)

@bp.route('/track/open/<token>')
def track_open(token):
    """Track email open with invisible pixel"""
    try:
        EmailTracker.track_email_open(token, request)
    except Exception as e:
        logger.error(f"Failed to track email open: {str(e)}")
    
    # Return a 1x1 transparent pixel
    pixel_data = b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\x00\x00\x00\x21\xF9\x04\x01\x00\x00\x00\x00\x2C\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x04\x01\x00\x3B'
    
    return Response(
        pixel_data,
        mimetype='image/gif',
        headers={
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0'
        }
    )

@bp.route('/track/click/<token>')
def track_click(token):
    """Track email click and redirect to simulation"""
    try:
        recipient = EmailTracker.track_email_click(token, request)
        if recipient and recipient.campaign:
            # Redirect to the phishing simulation with tracking token
            return redirect(url_for('simulations.phishing_email', 
                                  scenario_id=recipient.campaign.scenario_id, 
                                  t=token))
    except Exception as e:
        logger.error(f"Failed to track email click: {str(e)}")
    
    # Fallback redirect to main page
    return redirect(url_for('main.index'))

@bp.route('/track/report/<token>', methods=['POST'])
def track_report(token):
    """Track email report (user reported as phishing)"""
    try:
        success = EmailTracker.track_email_report(token)
        if success:
            return {'success': True, 'message': 'Thank you for reporting this phishing email!'}
        else:
            return {'success': False, 'message': 'Failed to record report'}, 400
    except Exception as e:
        logger.error(f"Failed to track email report: {str(e)}")
        return {'success': False, 'message': 'An error occurred'}, 500 