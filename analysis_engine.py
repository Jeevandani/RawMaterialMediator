import logging
import numpy as np
from typing import List, Dict, Any, Tuple
from models import ProcurementRequest

class AnalysisEngine:
    """Engine for analyzing vendors and providing recommendations"""
    
    def __init__(self):
        """Initialize analysis engine with default criteria weights"""
        # Criteria weights (quality: 30%, price: 25%, quantity: 25%, delivery: 20%)
        self.criteria_weights = {
            'quality': 0.30,
            'price': 0.25,
            'quantity': 0.25,
            'delivery': 0.20
        }
        
    def analyze_vendors(self, vendors: List[Dict[str, Any]], 
                       procurement_request: ProcurementRequest) -> Dict[str, Any]:
        """
        Perform comprehensive vendor analysis and ranking
        
        Args:
            vendors: List of vendor dictionaries
            procurement_request: The procurement request object
            
        Returns:
            Dictionary containing analysis results and rankings
        """
        if not vendors:
            return {
                'ranked_vendors': [],
                'analysis_summary': 'No vendors available for analysis',
                'criteria_weights': self.criteria_weights,
                'total_vendors_analyzed': 0
            }
        
        logging.info(f"Starting vendor analysis for {len(vendors)} vendors")
        
        # Calculate scores for each vendor
        vendor_scores = []
        for vendor in vendors:
            scores = self._calculate_vendor_scores(vendor, procurement_request)
            vendor_with_scores = vendor.copy()
            vendor_with_scores.update(scores)
            vendor_scores.append(vendor_with_scores)
        
        # Rank vendors by total score
        ranked_vendors = sorted(vendor_scores, key=lambda x: x['total_score'], reverse=True)
        
        # Generate analysis summary
        analysis_summary = self._generate_analysis_summary(ranked_vendors, procurement_request)
        
        # Calculate statistics
        stats = self._calculate_statistics(ranked_vendors)
        
        return {
            'ranked_vendors': ranked_vendors,
            'analysis_summary': analysis_summary,
            'criteria_weights': self.criteria_weights,
            'statistics': stats,
            'total_vendors_analyzed': len(vendors),
            'request_details': procurement_request.to_dict()
        }
    
    def _calculate_vendor_scores(self, vendor: Dict[str, Any], 
                                procurement_request: ProcurementRequest) -> Dict[str, float]:
        """
        Calculate individual and total scores for a vendor
        
        Args:
            vendor: Vendor dictionary
            procurement_request: The procurement request
            
        Returns:
            Dictionary with individual scores and total score
        """
        # Quality score (0-10 scale, normalized to 0-100)
        quality_score = (vendor['quality_rating'] / 10.0) * 100
        
        # Price score (inverse relationship - lower price is better)
        # Normalize against budget constraint
        price_ratio = vendor['price_per_unit'] / procurement_request.budget_constraint
        if price_ratio <= 1.0:
            # Within budget - score based on how much under budget
            price_score = (2.0 - price_ratio) * 50  # Max 100 if free, 50 if at budget
        else:
            # Over budget - penalty score
            price_score = max(0, 50 - (price_ratio - 1.0) * 50)
        
        # Quantity score - based on availability vs requirement
        quantity_ratio = vendor['quantity_available'] / procurement_request.quantity_required
        if quantity_ratio >= 1.0:
            # Can fulfill requirement
            quantity_score = min(100, 80 + (quantity_ratio - 1.0) * 10)  # Max 100
        else:
            # Cannot fully fulfill
            quantity_score = quantity_ratio * 80  # Proportional score up to 80
        
        # Delivery score (inverse relationship - faster delivery is better)
        # Convert delivery deadline to days for comparison
        delivery_urgency = self._parse_delivery_deadline(procurement_request.delivery_deadline)
        if vendor['delivery_time'] <= delivery_urgency:
            # Can meet deadline
            delivery_score = max(50, 100 - (vendor['delivery_time'] / delivery_urgency) * 50)
        else:
            # Cannot meet deadline
            delivery_score = max(0, 50 - ((vendor['delivery_time'] - delivery_urgency) / delivery_urgency) * 50)
        
        # Calculate weighted total score
        total_score = (
            quality_score * self.criteria_weights['quality'] +
            price_score * self.criteria_weights['price'] +
            quantity_score * self.criteria_weights['quantity'] +
            delivery_score * self.criteria_weights['delivery']
        )
        
        return {
            'quality_score': round(quality_score, 2),
            'price_score': round(price_score, 2),
            'quantity_score': round(quantity_score, 2),
            'delivery_score': round(delivery_score, 2),
            'total_score': round(total_score, 2)
        }
    
    def _parse_delivery_deadline(self, deadline: str) -> int:
        """
        Parse delivery deadline string and convert to days
        
        Args:
            deadline: Delivery deadline string
            
        Returns:
            Number of days as integer
        """
        deadline_lower = deadline.lower().strip()
        
        # Simple parsing logic for common deadline formats
        if 'urgent' in deadline_lower or 'asap' in deadline_lower:
            return 3
        elif 'week' in deadline_lower:
            if '1 week' in deadline_lower:
                return 7
            elif '2 week' in deadline_lower:
                return 14
            elif '3 week' in deadline_lower:
                return 21
            else:
                return 14  # Default to 2 weeks
        elif 'month' in deadline_lower:
            if '1 month' in deadline_lower:
                return 30
            elif '2 month' in deadline_lower:
                return 60
            elif '3 month' in deadline_lower:
                return 90
            else:
                return 30  # Default to 1 month
        else:
            # Try to extract number of days
            try:
                import re
                numbers = re.findall(r'\d+', deadline)
                if numbers:
                    return int(numbers[0])
            except:
                pass
            return 30  # Default fallback
    
    def _generate_analysis_summary(self, ranked_vendors: List[Dict[str, Any]], 
                                 procurement_request: ProcurementRequest) -> str:
        """
        Generate a comprehensive analysis summary
        
        Args:
            ranked_vendors: List of ranked vendors with scores
            procurement_request: The procurement request
            
        Returns:
            Analysis summary string
        """
        if not ranked_vendors:
            return "No vendors available for the requested material type."
        
        top_vendor = ranked_vendors[0]
        total_analyzed = len(ranked_vendors)
        
        # Budget analysis
        within_budget = sum(1 for v in ranked_vendors 
                          if v['price_per_unit'] <= procurement_request.budget_constraint)
        
        # Quality analysis
        high_quality = sum(1 for v in ranked_vendors if v['quality_rating'] >= 8.5)
        
        # Delivery analysis
        delivery_urgency = self._parse_delivery_deadline(procurement_request.delivery_deadline)
        can_deliver_on_time = sum(1 for v in ranked_vendors 
                                if v['delivery_time'] <= delivery_urgency)
        
        summary = f"""
Analysis Summary for {procurement_request.material_type.title()} Procurement:

• Total vendors analyzed: {total_analyzed}
• Vendors within budget (${procurement_request.budget_constraint:,.2f}/unit): {within_budget}
• High-quality vendors (8.5+ rating): {high_quality}  
• Vendors meeting delivery deadline: {can_deliver_on_time}

Top Recommendation: {top_vendor['name']}
• Overall Score: {top_vendor['total_score']:.1f}/100
• Quality Rating: {top_vendor['quality_rating']}/10
• Price: ${top_vendor['price_per_unit']:,.2f}/unit
• Available Quantity: {top_vendor['quantity_available']:,} units
• Delivery Time: {top_vendor['delivery_time']} days
• Location: {top_vendor['location']}

Key Strengths: This vendor offers {'excellent value' if top_vendor['price_score'] > 70 else 'competitive pricing'}, 
{'outstanding quality' if top_vendor['quality_score'] > 85 else 'good quality standards'}, and 
{'rapid delivery' if top_vendor['delivery_score'] > 80 else 'reasonable delivery times'}.
""".strip()
        
        return summary
    
    def _calculate_statistics(self, ranked_vendors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate statistical information about the vendor analysis
        
        Args:
            ranked_vendors: List of ranked vendors with scores
            
        Returns:
            Dictionary containing statistical data
        """
        if not ranked_vendors:
            return {}
        
        # Extract score arrays
        total_scores = [v['total_score'] for v in ranked_vendors]
        quality_scores = [v['quality_score'] for v in ranked_vendors]
        price_scores = [v['price_score'] for v in ranked_vendors]
        quantity_scores = [v['quantity_score'] for v in ranked_vendors]
        delivery_scores = [v['delivery_score'] for v in ranked_vendors]
        
        # Calculate statistics using NumPy
        stats = {
            'total_score': {
                'mean': float(np.mean(total_scores)),
                'median': float(np.median(total_scores)),
                'std': float(np.std(total_scores)),
                'min': float(np.min(total_scores)),
                'max': float(np.max(total_scores))
            },
            'quality_score': {
                'mean': float(np.mean(quality_scores)),
                'median': float(np.median(quality_scores))
            },
            'price_score': {
                'mean': float(np.mean(price_scores)),
                'median': float(np.median(price_scores))
            },
            'quantity_score': {
                'mean': float(np.mean(quantity_scores)),
                'median': float(np.median(quantity_scores))
            },
            'delivery_score': {
                'mean': float(np.mean(delivery_scores)),
                'median': float(np.median(delivery_scores))
            }
        }
        
        return stats
    
    def compare_vendors(self, vendor1: Dict[str, Any], vendor2: Dict[str, Any]) -> Dict[str, Any]:
        """
        Direct comparison between two vendors
        
        Args:
            vendor1: First vendor dictionary
            vendor2: Second vendor dictionary
            
        Returns:
            Comparison results dictionary
        """
        comparison = {
            'vendor1': vendor1['name'],
            'vendor2': vendor2['name'],
            'quality_comparison': 'vendor1' if vendor1['quality_rating'] > vendor2['quality_rating'] else 'vendor2',
            'price_comparison': 'vendor1' if vendor1['price_per_unit'] < vendor2['price_per_unit'] else 'vendor2',
            'quantity_comparison': 'vendor1' if vendor1['quantity_available'] > vendor2['quantity_available'] else 'vendor2',
            'delivery_comparison': 'vendor1' if vendor1['delivery_time'] < vendor2['delivery_time'] else 'vendor2',
            'quality_difference': abs(vendor1['quality_rating'] - vendor2['quality_rating']),
            'price_difference': abs(vendor1['price_per_unit'] - vendor2['price_per_unit']),
            'quantity_difference': abs(vendor1['quantity_available'] - vendor2['quantity_available']),
            'delivery_difference': abs(vendor1['delivery_time'] - vendor2['delivery_time'])
        }
        
        return comparison
