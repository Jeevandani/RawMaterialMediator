from flask import render_template, request, jsonify, flash, redirect, url_for, send_file
from flask_login import login_required, login_user, logout_user, current_user
from app import app, db
from models import ProcurementRequest, VendorAnalysis, Admin
from vendor_service import VendorService
from analysis_engine import AnalysisEngine
import json
import logging
from datetime import datetime
from functools import wraps
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# Initialize services
vendor_service = VendorService()
analysis_engine = AnalysisEngine()

# Admin authentication decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        admin = Admin.query.filter_by(username=username).first()
        
        if admin and admin.check_password(password):
            admin.last_login = datetime.utcnow()
            db.session.commit()
            login_user(admin)
            flash('Welcome back, Admin!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
@admin_required
def admin_logout():
    """Admin logout"""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Admin dashboard"""
    total_requests = ProcurementRequest.query.count()
    pending_requests = ProcurementRequest.query.filter_by(status='pending').count()
    analyzed_requests = ProcurementRequest.query.filter_by(status='analyzed').count()
    
    # Get recent analyses that need vendor selection
    pending_selections = VendorAnalysis.query.filter(
        VendorAnalysis.selected_vendor.is_(None)
    ).join(ProcurementRequest).order_by(VendorAnalysis.analysis_date.desc()).limit(10).all()
    
    # Get recent completed selections
    completed_selections = VendorAnalysis.query.filter(
        VendorAnalysis.selected_vendor.isnot(None)
    ).order_by(VendorAnalysis.selection_date.desc()).limit(10).all()
    
    return render_template('admin/dashboard.html',
                         total_requests=total_requests,
                         pending_requests=pending_requests,
                         analyzed_requests=analyzed_requests,
                         pending_selections=pending_selections,
                         completed_selections=completed_selections)

@app.route('/admin/select-vendor/<int:analysis_id>', methods=['POST'])
@admin_required
def select_vendor(analysis_id):
    """Admin selects final vendor"""
    analysis = VendorAnalysis.query.get_or_404(analysis_id)
    
    selected_vendor_id = request.form.get('vendor_id')
    selection_notes = request.form.get('notes', '')
    
    if not selected_vendor_id:
        flash('Please select a vendor', 'error')
        return redirect(url_for('analyze_vendors', request_id=analysis.request_id))
    
    # Get vendor details
    vendor = vendor_service.get_vendor_by_id(selected_vendor_id)
    if not vendor:
        flash('Invalid vendor selected', 'error')
        return redirect(url_for('analyze_vendors', request_id=analysis.request_id))
    
    # Update analysis with selection
    analysis.selected_vendor = vendor['name']
    analysis.selected_by = current_user.id
    analysis.selection_date = datetime.utcnow()
    analysis.selection_notes = selection_notes
    
    # Update request status
    analysis.request.status = 'vendor_selected'
    
    db.session.commit()
    
    flash(f'Vendor "{vendor["name"]}" has been selected successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/')
def index():
    """Home page with dashboard overview"""
    recent_requests = ProcurementRequest.query.order_by(ProcurementRequest.request_date.desc()).limit(5).all()
    return render_template('index.html', recent_requests=recent_requests)

@app.route('/request-form')
def request_form():
    """Display the procurement request form"""
    return render_template('request_form.html')

@app.route('/submit-request', methods=['POST'])
def submit_request():
    """Handle procurement request submission"""
    try:
        # Validate and collect form data
        material_type = request.form.get('material_type', '').strip()
        quantity_required = request.form.get('quantity_required', type=float)
        unit = request.form.get('unit', '').strip()
        quality_standard = request.form.get('quality_standard', '').strip()
        budget_constraint = request.form.get('budget_constraint', type=float)
        delivery_deadline = request.form.get('delivery_deadline', '').strip()
        additional_requirements = request.form.get('additional_requirements', '').strip()

        # Validation
        errors = []
        if not material_type:
            errors.append("Material type is required")
        if not quantity_required or quantity_required <= 0:
            errors.append("Valid quantity is required")
        if not unit:
            errors.append("Unit is required")
        if not quality_standard:
            errors.append("Quality standard is required")
        if not budget_constraint or budget_constraint <= 0:
            errors.append("Valid budget constraint is required")
        if not delivery_deadline:
            errors.append("Delivery deadline is required")

        if errors:
            for error in errors:
                flash(error, 'error')
            return redirect(url_for('request_form'))

        # Create new procurement request
        new_request = ProcurementRequest(
            material_type=material_type,
            quantity_required=quantity_required,
            unit=unit,
            quality_standard=quality_standard,
            budget_constraint=budget_constraint,
            delivery_deadline=delivery_deadline,
            additional_requirements=additional_requirements
        )
        
        db.session.add(new_request)
        db.session.commit()
        
        logging.info(f"New procurement request created with ID: {new_request.id}")
        flash('Procurement request submitted successfully!', 'success')
        
        return redirect(url_for('analyze_vendors', request_id=new_request.id))
        
    except Exception as e:
        logging.error(f"Error submitting request: {str(e)}")
        flash(f'Error submitting request: {str(e)}', 'error')
        return redirect(url_for('request_form'))

@app.route('/get-vendors/<int:request_id>')
def get_vendors(request_id):
    """Get available vendors for a specific material type"""
    try:
        procurement_request = ProcurementRequest.query.get_or_404(request_id)
        vendors = vendor_service.get_vendors_by_material(procurement_request.material_type)
        
        return jsonify({
            'success': True,
            'vendors': vendors,
            'count': len(vendors)
        })
        
    except Exception as e:
        logging.error(f"Error fetching vendors: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/analyze-vendors/<int:request_id>')
def analyze_vendors(request_id):
    """Analyze vendors and provide recommendations"""
    try:
        procurement_request = ProcurementRequest.query.get_or_404(request_id)
        
        # Check if analysis already exists
        existing_analysis = VendorAnalysis.query.filter_by(request_id=request_id).first()
        
        if existing_analysis:
            # Load existing analysis
            analysis_results = json.loads(existing_analysis.analysis_data)
            top_vendors = analysis_results.get('ranked_vendors', [])[:3]
            recommended_vendor = top_vendors[0] if top_vendors else None
            
            return render_template('analysis_results.html',
                                 request=procurement_request,
                                 vendors=top_vendors,
                                 analysis_results=analysis_results,
                                 recommended_vendor=recommended_vendor,
                                 analysis_record=existing_analysis)
        
        # Get vendors for the material type
        vendors = vendor_service.get_vendors_by_material(procurement_request.material_type)
        
        if not vendors:
            flash(f'No vendors found for material type: {procurement_request.material_type}', 'warning')
            return render_template('analysis_results.html', 
                                 request=procurement_request, 
                                 vendors=[], 
                                 analysis_results=None,
                                 recommended_vendor=None,
                                 analysis_record=None)
        
        # Perform analysis
        analysis_results = analysis_engine.analyze_vendors(vendors, procurement_request)
        
        # Get top 3 vendors
        top_vendors = analysis_results.get('ranked_vendors', [])[:3]
        recommended_vendor = top_vendors[0] if top_vendors else None
        
        # Save analysis to database
        analysis_record = VendorAnalysis(
            request_id=request_id,
            analysis_data=json.dumps(analysis_results),
            recommended_vendor=recommended_vendor['name'] if recommended_vendor else None
        )
        db.session.add(analysis_record)
        
        # Update request status
        procurement_request.status = 'analyzed'
        db.session.commit()
        
        logging.info(f"Vendor analysis completed for request ID: {request_id}")
        
        return render_template('analysis_results.html',
                             request=procurement_request,
                             vendors=top_vendors,
                             analysis_results=analysis_results,
                             recommended_vendor=recommended_vendor,
                             analysis_record=analysis_record)
        
    except Exception as e:
        logging.error(f"Error analyzing vendors: {str(e)}")
        flash(f'Error analyzing vendors: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/api/vendors/<material_type>')
def api_get_vendors(material_type):
    """API endpoint to get vendors by material type"""
    try:
        vendors = vendor_service.get_vendors_by_material(material_type)
        return jsonify({
            'success': True,
            'material_type': material_type,
            'vendors': vendors,
            'count': len(vendors)
        })
    except Exception as e:
        logging.error(f"API error fetching vendors: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/analysis/<int:request_id>')
def api_get_analysis(request_id):
    """API endpoint to get analysis results"""
    try:
        analysis = VendorAnalysis.query.filter_by(request_id=request_id).first()
        if not analysis:
            return jsonify({
                'success': False,
                'error': 'Analysis not found'
            }), 404
            
        return jsonify({
            'success': True,
            'analysis': json.loads(analysis.analysis_data),
            'recommended_vendor': analysis.recommended_vendor,
            'selected_vendor': analysis.selected_vendor,
            'analysis_date': analysis.analysis_date.isoformat()
        })
        
    except Exception as e:
        logging.error(f"API error fetching analysis: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/download-report/<int:request_id>')
def download_report(request_id):
    """Generate and download PDF report"""
    try:
        procurement_request = ProcurementRequest.query.get_or_404(request_id)
        analysis = VendorAnalysis.query.filter_by(request_id=request_id).first()
        
        if not analysis:
            flash('No analysis found for this request', 'error')
            return redirect(url_for('analyze_vendors', request_id=request_id))
        
        # Create PDF buffer
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title = Paragraph(f"Vendor Analysis Report - Request #{request_id}", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Request Summary
        story.append(Paragraph("Request Summary", styles['Heading2']))
        request_data = [
            ['Material Type:', procurement_request.material_type.title()],
            ['Quantity Required:', f"{procurement_request.quantity_required:,.0f} {procurement_request.unit}"],
            ['Budget Constraint:', f"${procurement_request.budget_constraint:,.2f}/unit"],
            ['Delivery Deadline:', procurement_request.delivery_deadline],
            ['Request Date:', procurement_request.request_date.strftime('%Y-%m-%d') if procurement_request.request_date else 'N/A']
        ]
        
        request_table = Table(request_data, colWidths=[120, 300])
        request_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(request_table)
        story.append(Spacer(1, 12))
        
        # Analysis Results
        analysis_data = json.loads(analysis.analysis_data)
        vendors = analysis_data.get('ranked_vendors', [])[:3]
        
        if vendors:
            story.append(Paragraph("Top Vendor Rankings", styles['Heading2']))
            
            vendor_data = [['Rank', 'Vendor Name', 'Total Score', 'Quality', 'Price', 'Quantity', 'Delivery']]
            for i, vendor in enumerate(vendors, 1):
                vendor_data.append([
                    str(i),
                    vendor['name'],
                    f"{vendor['total_score']:.1f}",
                    f"{vendor['quality_score']:.1f}",
                    f"{vendor['price_score']:.1f}",
                    f"{vendor['quantity_score']:.1f}",
                    f"{vendor['delivery_score']:.1f}"
                ])
            
            vendor_table = Table(vendor_data, colWidths=[40, 140, 60, 50, 50, 50, 50])
            vendor_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(vendor_table)
            story.append(Spacer(1, 12))
        
        # Selection Status
        story.append(Paragraph("Selection Status", styles['Heading2']))
        if analysis.selected_vendor:
            selection_info = f"Selected Vendor: {analysis.selected_vendor}"
            if analysis.selection_date:
                selection_info += f"\nSelection Date: {analysis.selection_date.strftime('%Y-%m-%d %H:%M')}"
            if analysis.selection_notes:
                selection_info += f"\nNotes: {analysis.selection_notes}"
            story.append(Paragraph(selection_info, styles['Normal']))
        else:
            story.append(Paragraph("Status: Pending admin selection", styles['Normal']))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f'vendor_analysis_report_{request_id}.pdf',
            mimetype='application/pdf'
        )
        
    except Exception as e:
        logging.error(f"Error generating PDF report: {str(e)}")
        flash(f'Error generating report: {str(e)}', 'error')
        return redirect(url_for('analyze_vendors', request_id=request_id))

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('base.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    db.session.rollback()
    return render_template('base.html'), 500
