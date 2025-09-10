"""
Vercel API endpoint for associate management automation.
Handles associate assignments, performance tracking, commission calculations, and workload management.
"""

from http.server import BaseHTTPRequestHandler
import json
import os
import sys
from urllib.parse import urlparse, parse_qs
from typing import Dict, Any, List
from datetime import datetime, timedelta

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle POST requests for associate automation."""
        try:
            # Get content length
            content_length = int(self.headers.get('Content-Length', 0))
            
            # Read the request body
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                try:
                    payload = json.loads(post_data.decode('utf-8'))
                except json.JSONDecodeError:
                    self.send_error_response(400, "Invalid JSON payload")
                    return
            else:
                self.send_error_response(400, "No request body")
                return
            
            # Process associate automation
            trigger_type = payload.get('triggerType', 'performance_review')
            associate_data = payload
            
            results = {
                'trigger_type': trigger_type,
                'associate_id': associate_data.get('associateId', ''),
                'associate_name': associate_data.get('associateName', ''),
                'updated_load': 0,
                'performance_score': 0,
                'commission_calculated': 0,
                'recommendations': [],
                'alerts': [],
                'processed_timestamp': datetime.utcnow().isoformat()
            }
            
            # Process based on trigger type
            if trigger_type == 'performance_review':
                review_results = self.process_performance_review(associate_data)
                results.update(review_results)
                
            elif trigger_type == 'workload_assignment':
                assignment_results = self.process_workload_assignment(associate_data)
                results.update(assignment_results)
                
            elif trigger_type == 'commission_calculation':
                commission_results = self.process_commission_calculation(associate_data)
                results.update(commission_results)
            
            # Send success response
            response_data = {
                'success': True,
                **results,
                'automation_type': 'associate_automation'
            }
            
            self.send_json_response(200, response_data)
            
        except Exception as e:
            error_response = {
                'success': False,
                'error': str(e),
                'error_type': 'associate_automation_error',
                'timestamp': datetime.utcnow().isoformat()
            }
            self.send_json_response(500, error_response)
    
    def process_performance_review(self, associate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process associate performance review and generate recommendations."""
        
        associate_name = associate_data.get('associateName', '')
        current_load = associate_data.get('currentLoad', 0)
        current_performance = associate_data.get('performanceScore', 75)
        specialization = associate_data.get('specialization', '')
        
        # Mock session performance data (would query actual sessions in real implementation)
        recent_sessions = self.get_mock_session_performance(associate_name)
        
        # Calculate updated performance score
        updated_performance = self.calculate_performance_score(
            current_performance, recent_sessions, current_load
        )
        
        # Generate recommendations
        recommendations = self.generate_performance_recommendations(
            associate_name, updated_performance, current_load, specialization, recent_sessions
        )
        
        # Generate alerts for performance issues
        alerts = self.generate_performance_alerts(
            associate_name, updated_performance, current_load, recent_sessions
        )
        
        # Calculate optimal workload
        optimal_load = self.calculate_optimal_workload(updated_performance, specialization)
        
        return {
            'updated_load': current_load,  # Would update based on assignments
            'performance_score': updated_performance,
            'optimal_workload': optimal_load,
            'recent_session_count': len(recent_sessions),
            'average_client_rating': sum(s['client_rating'] for s in recent_sessions) / len(recent_sessions) if recent_sessions else 0,
            'recommendations': recommendations,
            'alerts': alerts,
            'recommended_specialization': self.recommend_specialization_focus(recent_sessions, specialization)
        }
    
    def process_workload_assignment(self, associate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process workload assignment and balancing."""
        
        associate_name = associate_data.get('associateName', '')
        current_load = associate_data.get('currentLoad', 0)
        specialization = associate_data.get('specialization', '')
        performance_score = associate_data.get('performanceScore', 75)
        
        # Mock available assignments (would query actual deals/sessions in real implementation)
        available_assignments = self.get_mock_available_assignments()
        
        # Calculate assignment suitability
        suitable_assignments = []
        for assignment in available_assignments:
            suitability_score = self.calculate_assignment_suitability(
                assignment, specialization, current_load, performance_score
            )
            if suitability_score > 0.6:
                assignment['suitability_score'] = suitability_score
                suitable_assignments.append(assignment)
        
        # Sort by suitability
        suitable_assignments.sort(key=lambda x: x['suitability_score'], reverse=True)
        
        # Calculate new load if assignments are accepted
        potential_new_load = current_load
        recommended_assignments = []
        
        for assignment in suitable_assignments[:3]:  # Top 3 assignments
            if potential_new_load + assignment['estimated_hours'] <= self.get_max_workload(performance_score):
                recommended_assignments.append(assignment)
                potential_new_load += assignment['estimated_hours']
        
        return {
            'current_load': current_load,
            'updated_load': potential_new_load,
            'available_assignments': len(available_assignments),
            'suitable_assignments': len(suitable_assignments),
            'recommended_assignments': recommended_assignments,
            'workload_capacity': self.get_max_workload(performance_score) - current_load,
            'recommendations': [
                f"Consider assignment: {assignment['client_name']} - {assignment['type']}" 
                for assignment in recommended_assignments
            ]
        }
    
    def process_commission_calculation(self, associate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process commission calculations for associate."""
        
        associate_name = associate_data.get('associateName', '')
        rate = associate_data.get('rate', 150)
        
        # Mock completed sessions for commission calculation
        completed_sessions = self.get_mock_completed_sessions(associate_name)
        
        total_commission = 0
        session_commissions = []
        
        for session in completed_sessions:
            # Calculate commission based on session type and performance
            session_commission = self.calculate_session_commission(
                session, rate, associate_data.get('performanceScore', 75)
            )
            
            session_commissions.append({
                'session_id': session['id'],
                'client_name': session['client_name'],
                'session_date': session['date'],
                'base_rate': rate,
                'performance_multiplier': session_commission['multiplier'],
                'commission_amount': session_commission['amount']
            })
            
            total_commission += session_commission['amount']
        
        # Calculate monthly performance bonus
        performance_bonus = self.calculate_performance_bonus(
            associate_data.get('performanceScore', 75), 
            len(completed_sessions), 
            total_commission
        )
        
        return {
            'commission_calculated': total_commission,
            'performance_bonus': performance_bonus,
            'total_earnings': total_commission + performance_bonus,
            'sessions_completed': len(completed_sessions),
            'session_commissions': session_commissions,
            'average_commission_per_session': total_commission / len(completed_sessions) if completed_sessions else 0,
            'recommendations': [
                f"Total commission earned: ${total_commission:,.2f}",
                f"Performance bonus: ${performance_bonus:,.2f}",
                f"Sessions delivered: {len(completed_sessions)}"
            ]
        }
    
    def get_mock_session_performance(self, associate_name: str) -> List[Dict[str, Any]]:
        """Mock recent session performance data."""
        import random
        
        sessions = []
        for i in range(random.randint(3, 8)):
            sessions.append({
                'session_id': f'sess_{i+1}',
                'client_name': f'Client {chr(65+i)}',
                'date': (datetime.utcnow() - timedelta(days=random.randint(1, 30))).isoformat(),
                'duration': random.randint(60, 120),
                'client_rating': random.uniform(3.5, 5.0),
                'session_type': random.choice(['Executive Coaching', 'Team Development', 'Leadership Assessment']),
                'completion_status': random.choice(['Completed', 'Completed', 'Completed', 'Rescheduled'])
            })
        
        return sessions
    
    def calculate_performance_score(self, current_score: float, sessions: List[Dict], current_load: int) -> float:
        """Calculate updated performance score based on recent activity."""
        
        if not sessions:
            return max(current_score - 5, 0)  # Decline if no sessions
        
        # Calculate session-based metrics
        completed_sessions = [s for s in sessions if s['completion_status'] == 'Completed']
        avg_rating = sum(s['client_rating'] for s in completed_sessions) / len(completed_sessions) if completed_sessions else 0
        completion_rate = len(completed_sessions) / len(sessions)
        
        # Base score from client ratings (0-100 scale)
        rating_score = (avg_rating / 5.0) * 100
        
        # Completion rate bonus/penalty
        completion_bonus = (completion_rate - 0.9) * 50  # Bonus for >90% completion
        
        # Workload efficiency (optimal range 20-40 hours)
        if 20 <= current_load <= 40:
            load_bonus = 10
        elif current_load > 40:
            load_bonus = -5  # Overloaded penalty
        else:
            load_bonus = -2  # Under-utilized penalty
        
        new_score = (current_score * 0.7) + (rating_score * 0.2) + completion_bonus + load_bonus
        return max(0, min(100, new_score))
    
    def generate_performance_recommendations(self, name: str, score: float, load: int, specialization: str, sessions: List[Dict]) -> List[str]:
        """Generate performance improvement recommendations."""
        
        recommendations = []
        
        if score < 70:
            recommendations.append(f"{name} should focus on improving client satisfaction scores")
            recommendations.append("Consider additional training in client communication")
        
        if load > 40:
            recommendations.append(f"{name} may be overloaded - consider redistributing some sessions")
        elif load < 15:
            recommendations.append(f"{name} has capacity for additional assignments")
        
        # Session-specific recommendations
        completed_sessions = [s for s in sessions if s['completion_status'] == 'Completed']
        if len(completed_sessions) > 0:
            avg_rating = sum(s['client_rating'] for s in completed_sessions) / len(completed_sessions)
            if avg_rating < 4.0:
                recommendations.append("Focus on session preparation and follow-up quality")
        
        # Specialization recommendations
        session_types = [s['session_type'] for s in sessions]
        most_common_type = max(set(session_types), key=session_types.count) if session_types else None
        if most_common_type and most_common_type != specialization:
            recommendations.append(f"Consider specializing more in {most_common_type} based on recent session types")
        
        return recommendations
    
    def generate_performance_alerts(self, name: str, score: float, load: int, sessions: List[Dict]) -> List[str]:
        """Generate alerts for performance issues."""
        
        alerts = []
        
        if score < 60:
            alerts.append(f"CRITICAL: {name} performance score below 60% - immediate attention required")
        elif score < 75:
            alerts.append(f"WARNING: {name} performance score declining - monitor closely")
        
        if load > 45:
            alerts.append(f"ALERT: {name} workload exceeds recommended maximum - risk of burnout")
        
        # Check for recent cancellations
        cancelled_sessions = [s for s in sessions if s['completion_status'] != 'Completed']
        if len(cancelled_sessions) / len(sessions) > 0.2:
            alerts.append(f"ALERT: {name} has high cancellation rate - investigate scheduling issues")
        
        return alerts
    
    def get_mock_available_assignments(self) -> List[Dict[str, Any]]:
        """Mock available assignment opportunities."""
        
        return [
            {
                'client_name': 'TechCorp Executive',
                'type': 'Executive Coaching',
                'estimated_hours': 8,
                'specialization_match': 'Executive Coaching',
                'priority': 'High',
                'start_date': (datetime.utcnow() + timedelta(days=7)).isoformat()
            },
            {
                'client_name': 'StartupXYZ Team',
                'type': 'Team Development',
                'estimated_hours': 12,
                'specialization_match': 'Team Development',
                'priority': 'Medium',
                'start_date': (datetime.utcnow() + timedelta(days=14)).isoformat()
            },
            {
                'client_name': 'Global Industries',
                'type': 'Leadership Assessment',
                'estimated_hours': 6,
                'specialization_match': 'Leadership Assessment',
                'priority': 'Low',
                'start_date': (datetime.utcnow() + timedelta(days=21)).isoformat()
            }
        ]
    
    def calculate_assignment_suitability(self, assignment: Dict, specialization: str, current_load: int, performance_score: float) -> float:
        """Calculate how suitable an assignment is for the associate."""
        
        suitability = 0.5  # Base score
        
        # Specialization match
        if assignment['specialization_match'] == specialization:
            suitability += 0.3
        
        # Workload capacity
        max_load = self.get_max_workload(performance_score)
        if current_load + assignment['estimated_hours'] <= max_load:
            suitability += 0.2
        else:
            suitability -= 0.3  # Penalize overloading
        
        # Performance requirement
        if performance_score >= 80:
            suitability += 0.1
        elif performance_score < 65:
            suitability -= 0.2
        
        # Priority adjustment
        if assignment['priority'] == 'High':
            suitability += 0.1
        
        return max(0, min(1, suitability))
    
    def get_max_workload(self, performance_score: float) -> int:
        """Get maximum recommended workload based on performance."""
        
        if performance_score >= 85:
            return 45  # High performers can handle more
        elif performance_score >= 75:
            return 35  # Standard load
        else:
            return 25  # Reduced load for improvement
    
    def get_mock_completed_sessions(self, associate_name: str) -> List[Dict[str, Any]]:
        """Mock completed sessions for commission calculation."""
        import random
        
        sessions = []
        for i in range(random.randint(4, 10)):
            sessions.append({
                'id': f'session_{i+1}',
                'client_name': f'Client {chr(65+i)}',
                'date': (datetime.utcnow() - timedelta(days=random.randint(1, 30))).date().isoformat(),
                'session_type': random.choice(['Executive Coaching', 'Team Development', 'Leadership Assessment']),
                'duration': random.randint(60, 120),
                'client_rating': random.uniform(3.5, 5.0),
                'base_rate': 150
            })
        
        return sessions
    
    def calculate_session_commission(self, session: Dict, base_rate: float, performance_score: float) -> Dict[str, Any]:
        """Calculate commission for a specific session."""
        
        # Base commission is the hourly rate
        base_commission = base_rate
        
        # Performance multiplier (0.8 to 1.2)
        performance_multiplier = 0.8 + (performance_score / 100) * 0.4
        
        # Client rating bonus
        rating_bonus = max(0, (session['client_rating'] - 4.0) * 0.1)
        
        # Session type multiplier
        type_multipliers = {
            'Executive Coaching': 1.2,
            'Team Development': 1.1,
            'Leadership Assessment': 1.0
        }
        type_multiplier = type_multipliers.get(session['session_type'], 1.0)
        
        final_multiplier = performance_multiplier + rating_bonus
        final_commission = base_commission * type_multiplier * final_multiplier
        
        return {
            'amount': round(final_commission, 2),
            'multiplier': round(final_multiplier, 3),
            'type_multiplier': type_multiplier,
            'performance_component': round(performance_multiplier, 3),
            'rating_bonus': round(rating_bonus, 3)
        }
    
    def calculate_performance_bonus(self, performance_score: float, sessions_count: int, total_commission: float) -> float:
        """Calculate performance bonus."""
        
        bonus = 0
        
        # High performance bonus
        if performance_score >= 90:
            bonus += total_commission * 0.1  # 10% bonus
        elif performance_score >= 80:
            bonus += total_commission * 0.05  # 5% bonus
        
        # Volume bonus
        if sessions_count >= 10:
            bonus += 200  # Flat bonus for high volume
        elif sessions_count >= 5:
            bonus += 100
        
        return round(bonus, 2)
    
    def calculate_optimal_workload(self, performance_score: float, specialization: str) -> int:
        """Calculate optimal workload recommendation."""
        
        base_load = 30
        
        # Adjust for performance
        if performance_score >= 85:
            base_load += 10
        elif performance_score < 70:
            base_load -= 10
        
        # Adjust for specialization complexity
        complex_specializations = ['Executive Coaching', 'Leadership Assessment']
        if specialization in complex_specializations:
            base_load -= 5
        
        return max(15, min(45, base_load))
    
    def recommend_specialization_focus(self, sessions: List[Dict], current_specialization: str) -> str:
        """Recommend specialization focus based on recent session performance."""
        
        if not sessions:
            return current_specialization
        
        # Analyze session types and ratings
        type_performance = {}
        for session in sessions:
            session_type = session['session_type']
            if session_type not in type_performance:
                type_performance[session_type] = []
            type_performance[session_type].append(session['client_rating'])
        
        # Calculate average rating per type
        type_averages = {
            t: sum(ratings) / len(ratings) 
            for t, ratings in type_performance.items()
        }
        
        # Recommend the type with highest performance
        if type_averages:
            best_type = max(type_averages, key=type_averages.get)
            if type_averages[best_type] > 4.2 and best_type != current_specialization:
                return f"Consider focusing more on {best_type} (avg rating: {type_averages[best_type]:.1f})"
        
        return current_specialization
    
    def send_json_response(self, status_code: int, data: Dict[str, Any]):
        """Send JSON response with proper headers."""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        response_json = json.dumps(data, indent=2)
        self.wfile.write(response_json.encode('utf-8'))
    
    def send_error_response(self, status_code: int, message: str):
        """Send error response."""
        error_data = {
            'success': False,
            'error': message,
            'timestamp': datetime.utcnow().isoformat()
        }
        self.send_json_response(status_code, error_data)
    
    def do_GET(self):
        """Handle GET requests - return API information."""
        info_data = {
            'service': 'Associate Management Automation API',
            'version': '1.0.0',
            'description': 'Handles associate assignments, performance tracking, and commission calculations',
            'trigger_types': ['performance_review', 'workload_assignment', 'commission_calculation'],
            'features': [
                'Performance score calculation based on client ratings',
                'Workload optimization and assignment recommendations',
                'Commission calculation with performance multipliers',
                'Specialization focus recommendations',
                'Performance alerts and improvement suggestions'
            ],
            'methods': ['POST'],
            'status': 'active',
            'timestamp': datetime.utcnow().isoformat()
        }
        self.send_json_response(200, info_data)
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()