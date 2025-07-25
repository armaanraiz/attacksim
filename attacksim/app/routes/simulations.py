from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, abort
from flask_login import login_required, current_user
from app import db
from app.models import Scenario, Interaction
from app.models.scenario import ScenarioType
from app.models.interaction import InteractionType, InteractionResult

bp = Blueprint('simulations', __name__)

@bp.route('/phishing/<int:scenario_id>')
def phishing_email(scenario_id):
    """Display phishing email simulation"""
    scenario = Scenario.query.get_or_404(scenario_id)
    
    if scenario.scenario_type != ScenarioType.PHISHING_EMAIL:
        abort(404)
    
    if not scenario.is_active():
        return render_template('simulations/scenario_inactive.html')
    
    # Check if this is from an email campaign tracking
    tracking_token = request.args.get('t')
    email_recipient = None
    
    if tracking_token:
        from app.models import EmailRecipient
        email_recipient = EmailRecipient.query.filter_by(unique_token=tracking_token).first()
        if email_recipient:
            # Mark as clicked if not already done
            if not email_recipient.clicked_at:
                email_recipient.mark_clicked()
    
    # Create interaction record
    interaction = None
    if current_user.is_authenticated:
        interaction = Interaction(
            user_id=current_user.id,
            scenario_id=scenario.id,
            interaction_type=InteractionType.EMAIL_CLICKED if tracking_token else InteractionType.EMAIL_OPENED,
            result=InteractionResult.PARTIAL,  # Will be updated based on user action
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string
        )
        db.session.add(interaction)
        db.session.commit()
    
    return render_template('simulations/phishing_email.html', 
                         scenario=scenario,
                         interaction_id=interaction.id if interaction else None,
                         tracking_token=tracking_token,
                         from_email_campaign=bool(email_recipient))

@bp.route('/fake-login/<int:scenario_id>')
def fake_login(scenario_id):
    """Display fake login page simulation"""
    scenario = Scenario.query.get_or_404(scenario_id)
    
    if scenario.scenario_type != ScenarioType.FAKE_LOGIN:
        abort(404)
    
    if not scenario.is_active():
        return render_template('simulations/scenario_inactive.html')
    
    # Create interaction record
    if current_user.is_authenticated:
        interaction = Interaction(
            user_id=current_user.id,
            scenario_id=scenario.id,
            interaction_type=InteractionType.LOGIN_ATTEMPTED,
            result=InteractionResult.PARTIAL,
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string
        )
        db.session.add(interaction)
        db.session.commit()
    
    # Determine which template to use based on target website
    template_name = f'simulations/fake_login_{scenario.login_template}.html'
    
    return render_template(template_name, 
                         scenario=scenario,
                         interaction_id=interaction.id if current_user.is_authenticated else None)

@bp.route('/suspicious-link/<int:scenario_id>')
def suspicious_link(scenario_id):
    """Display suspicious link simulation"""
    scenario = Scenario.query.get_or_404(scenario_id)
    
    if scenario.scenario_type != ScenarioType.SUSPICIOUS_LINK:
        abort(404)
    
    if not scenario.is_active():
        return render_template('simulations/scenario_inactive.html')
    
    # Create interaction record
    if current_user.is_authenticated:
        interaction = Interaction(
            user_id=current_user.id,
            scenario_id=scenario.id,
            interaction_type=InteractionType.LINK_CLICKED,
            result=InteractionResult.PARTIAL,
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string,
            clicked_url=scenario.malicious_url
        )
        db.session.add(interaction)
        db.session.commit()
    
    return render_template('simulations/suspicious_link.html', 
                         scenario=scenario,
                         interaction_id=interaction.id if current_user.is_authenticated else None)

@bp.route('/interact', methods=['POST'])
@login_required
def record_interaction():
    """Record user interaction with simulation"""
    interaction_id = request.form.get('interaction_id')
    action = request.form.get('action')
    submitted_data = request.form.get('submitted_data')
    
    if not interaction_id:
        return jsonify({'error': 'Invalid interaction'}), 400
    
    interaction = Interaction.query.get_or_404(interaction_id)
    
    if interaction.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Determine result based on action
    if action == 'report_suspicious':
        interaction.record_threat_reported()
        scenario = interaction.scenario
        scenario.increment_stats(detected=True)
        
        return jsonify({
            'success': True,
            'message': 'Great job! You correctly identified this as a threat.',
            'show_education': True,
            'education_content': scenario.educational_message
        })
    
    elif action == 'click_link' or action == 'submit_credentials':
        interaction.result = InteractionResult.FELL_FOR_IT
        interaction.detected_threat = False
        if submitted_data:
            interaction.submitted_data = submitted_data
        interaction.mark_completed()
        
        scenario = interaction.scenario
        scenario.increment_stats(detected=False)
        
        return jsonify({
            'success': True,
            'message': 'This was a simulated attack! You fell for it, but that\'s okay - it\'s a learning opportunity.',
            'show_education': True,
            'education_content': scenario.educational_message,
            'fell_for_it': True
        })
    
    elif action == 'ignore' or action == 'delete':
        interaction.result = InteractionResult.DETECTED
        interaction.detected_threat = True
        interaction.mark_completed()
        
        scenario = interaction.scenario
        scenario.increment_stats(detected=True)
        
        return jsonify({
            'success': True,
            'message': 'Good instinct! Ignoring suspicious content is often the right choice.',
            'show_education': True,
            'education_content': scenario.educational_message
        })
    
    return jsonify({'error': 'Invalid action'}), 400

@bp.route('/education/<int:interaction_id>')
@login_required
def view_education(interaction_id):
    """Display educational content after simulation"""
    interaction = Interaction.query.get_or_404(interaction_id)
    
    if interaction.user_id != current_user.id:
        abort(403)
    
    scenario = interaction.scenario
    
    # Record that user viewed education
    interaction.record_education_viewed()
    
    return render_template('simulations/education.html', 
                         scenario=scenario,
                         interaction=interaction)

@bp.route('/feedback/<int:interaction_id>', methods=['GET', 'POST'])
@login_required
def feedback(interaction_id):
    """Collect user feedback on simulation"""
    interaction = Interaction.query.get_or_404(interaction_id)
    
    if interaction.user_id != current_user.id:
        abort(403)
    
    if request.method == 'POST':
        feedback_text = request.form.get('feedback')
        confidence_level = request.form.get('confidence_level')
        
        interaction.user_feedback = feedback_text
        if confidence_level:
            interaction.confidence_level = int(confidence_level)
        
        db.session.commit()
        
        flash('Thank you for your feedback!', 'success')
        return redirect(url_for('main.dashboard'))
    
    return render_template('simulations/feedback.html', 
                         interaction=interaction,
                         scenario=interaction.scenario)

@bp.route('/report-threat', methods=['POST'])
@login_required
def report_threat():
    """Allow users to report suspicious content they encounter"""
    url = request.form.get('url')
    description = request.form.get('description')
    
    if not url or not description:
        return jsonify({'error': 'URL and description are required'}), 400
    
    # In a real implementation, this would create a threat report
    # For now, we'll just acknowledge the report
    
    flash('Thank you for reporting this suspicious content. Our security team will investigate.', 'success')
    return jsonify({'success': True, 'message': 'Threat reported successfully'})

@bp.route('/simulation-complete/<int:interaction_id>')
@login_required
def simulation_complete(interaction_id):
    """Display completion page with summary"""
    interaction = Interaction.query.get_or_404(interaction_id)
    
    if interaction.user_id != current_user.id:
        abort(403)
    
    scenario = interaction.scenario
    user_stats = current_user.get_interaction_stats()
    
    return render_template('simulations/complete.html',
                         interaction=interaction,
                         scenario=scenario,
                         user_stats=user_stats)

@bp.route('/api/track-time', methods=['POST'])
@login_required
def track_time():
    """Track time spent on educational content"""
    interaction_id = request.json.get('interaction_id')
    time_spent = request.json.get('time_spent')
    
    if not interaction_id or not time_spent:
        return jsonify({'error': 'Missing parameters'}), 400
    
    interaction = Interaction.query.get_or_404(interaction_id)
    
    if interaction.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    interaction.education_time_spent = time_spent
    db.session.commit()
    
    return jsonify({'success': True}) 