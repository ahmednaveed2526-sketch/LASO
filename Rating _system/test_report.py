# testing_report.py
from datetime import datetime
from typing import List, Dict, Optional
import json
from rating_system import RatingSystem
from models import ServiceCategory

class TestingReport:
    def __init__(self):
        self.rating_system = RatingSystem()
        self.tests_run = []
        self.passed_tests = []
        self.failed_tests = []
        self.test_results = {}
    
    def run_all_tests(self):
        """Run all test scenarios and generate report"""
        print("\n" + "="*60)
        print("RUNNING TEST SUITE FOR RATINGS & TESTING COORDINATOR")
        print("="*60)
        
        # Test 1: Rating submission
        self._test_rating_submission()
        
        # Test 2: Review submission
        self._test_review_submission()
        
        # Test 3: Provider statistics
        self._test_provider_statistics()
        
        # Test 4: Category averages
        self._test_category_averages()
        
        # Test 5: Customer ratings retrieval
        self._test_customer_ratings()
        
        # Test 6: Edge cases
        self._test_edge_cases()
        
        # Test 7: Data persistence
        self._test_data_persistence()
        
        # Test 8: Review helpfulness
        self._test_review_helpfulness()
        
        # Generate summary
        self._generate_summary()
    
    def _record_test(self, test_name: str, passed: bool, details: str = ""):
        """Record test results"""
        self.tests_run.append(test_name)
        if passed:
            self.passed_tests.append(test_name)
        else:
            self.failed_tests.append(test_name)
        
        self.test_results[test_name] = {
            'passed': passed,
            'timestamp': datetime.now().isoformat(),
            'details': details
        }
    
    def _test_rating_submission(self):
        """Test rating submission functionality"""
        print("\n--- Test 1: Rating Submission ---")
        
        try:
            # Test valid rating
            result = self.rating_system.submit_rating(
                service_id=1,
                customer_id=101,
                provider_id=201,
                rating=4.5,
                comment="Great service, very professional!",
                category=ServiceCategory.PLUMBING
            )
            
            if result:
                self._record_test("Valid rating submission", True, 
                                 "Rating 4.5 submitted successfully")
            else:
                self._record_test("Valid rating submission", False, 
                                 "Rating submission failed")
            
            # Test invalid rating
            result = self.rating_system.submit_rating(
                service_id=1,
                customer_id=101,
                provider_id=201,
                rating=6.0,
                comment="Should fail",
                category=ServiceCategory.PLUMBING
            )
            
            if not result:
                self._record_test("Invalid rating rejection", True, 
                                 "6.0 rating correctly rejected")
            else:
                self._record_test("Invalid rating rejection", False, 
                                 "Should have rejected 6.0 rating")
                
        except Exception as e:
            self._record_test("Rating submission", False, f"Exception: {str(e)}")
    
    def _test_review_submission(self):
        """Test review submission functionality"""
        print("\n--- Test 2: Review Submission ---")
        
        try:
            # First submit a rating
            self.rating_system.submit_rating(
                service_id=2,
                customer_id=102,
                provider_id=202,
                rating=5.0,
                comment="Excellent work!",
                category=ServiceCategory.ELECTRICAL
            )
            
            # Submit review for the rating
            result = self.rating_system.submit_review(
                rating_id=2,
                reviewer_id=301,
                review_text="Very satisfied with the service. Professional and timely."
            )
            
            if result:
                self._record_test("Review submission", True, 
                                 "Review submitted successfully")
            else:
                self._record_test("Review submission", False, 
                                 "Review submission failed")
            
            # Test review for non-existent rating
            result = self.rating_system.submit_review(
                rating_id=999,
                reviewer_id=301,
                review_text="Should fail"
            )
            
            if not result:
                self._record_test("Invalid review rejection", True, 
                                 "Review for non-existent rating rejected")
            else:
                self._record_test("Invalid review rejection", False, 
                                 "Should have rejected review for non-existent rating")
                
        except Exception as e:
            self._record_test("Review submission", False, f"Exception: {str(e)}")
    
    def _test_provider_statistics(self):
        """Test provider statistics calculation"""
        print("\n--- Test 3: Provider Statistics ---")
        
        try:
            # Submit multiple ratings for a provider
            for i in range(5):
                self.rating_system.submit_rating(
                    service_id=100+i,
                    customer_id=200+i,
                    provider_id=203,
                    rating=3.0 + i * 0.5,
                    comment=f"Service {i+1}",
                    category=ServiceCategory.CLEANING
                )
            
            stats = self.rating_system.get_provider_stats(203)
            
            if stats['total_ratings'] == 5 and stats['average_rating'] > 0:
                self._record_test("Provider statistics", True, 
                                 f"Total: {stats['total_ratings']}, Average: {stats['average_rating']:.2f}")
            else:
                self._record_test("Provider statistics", False, 
                                 "Statistics calculation error")
                
        except Exception as e:
            self._record_test("Provider statistics", False, f"Exception: {str(e)}")
    
    def _test_category_averages(self):
        """Test category average calculation"""
        print("\n--- Test 4: Category Averages ---")
        
        try:
            # Submit ratings for different categories
            categories = [
                ServiceCategory.PLUMBING,
                ServiceCategory.ELECTRICAL,
                ServiceCategory.CARPENTRY
            ]
            
            for i, category in enumerate(categories):
                self.rating_system.submit_rating(
                    service_id=200+i,
                    customer_id=300+i,
                    provider_id=400+i,
                    rating=4.0 + i,
                    comment=f"Category {category.value}",
                    category=category
                )
            
            avg_plumbing = self.rating_system.get_category_average(ServiceCategory.PLUMBING)
            avg_electrical = self.rating_system.get_category_average(ServiceCategory.ELECTRICAL)
            
            if avg_plumbing == 4.0 and avg_electrical == 5.0:
                self._record_test("Category averages", True, 
                                 "All category averages correct")
            else:
                self._record_test("Category averages", False, 
                                 f"Plumbing: {avg_plumbing}, Electrical: {avg_electrical}")
                
        except Exception as e:
            self._record_test("Category averages", False, f"Exception: {str(e)}")
    
    def _test_customer_ratings(self):
        """Test customer ratings retrieval"""
        print("\n--- Test 5: Customer Ratings ---")
        
        try:
            customer_id = 105
            
            for i in range(3):
                self.rating_system.submit_rating(
                    service_id=300+i,
                    customer_id=customer_id,
                    provider_id=500+i,
                    rating=4.0 + i * 0.5,
                    comment=f"Customer service {i+1}",
                    category=ServiceCategory.PAINTING
                )
            
            customer_ratings = self.rating_system.get_customer_ratings(customer_id)
            
            if len(customer_ratings) == 3:
                self._record_test("Customer ratings retrieval", True, 
                                 f"Found {len(customer_ratings)} ratings")
            else:
                self._record_test("Customer ratings retrieval", False, 
                                 f"Expected 3, found {len(customer_ratings)}")
                
        except Exception as e:
            self._record_test("Customer ratings retrieval", False, f"Exception: {str(e)}")
    
    def _test_edge_cases(self):
        """Test edge cases"""
        print("\n--- Test 6: Edge Cases ---")
        
        try:
            # Test minimum and maximum ratings
            test_cases = [
                (1.0, "Minimum rating"),
                (5.0, "Maximum rating"),
                (2.5, "Mid-point rating")
            ]
            
            all_passed = True
            for rating_val, description in test_cases:
                result = self.rating_system.submit_rating(
                    service_id=400,
                    customer_id=106,
                    provider_id=601,
                    rating=rating_val,
                    comment=f"Test {description}",
                    category=ServiceCategory.HVAC
                )
                if not result:
                    all_passed = False
                    break
            
            if all_passed:
                self._record_test("Edge cases - rating boundaries", True, 
                                 "All boundary ratings accepted")
            else:
                self._record_test("Edge cases - rating boundaries", False, 
                                 "Some boundary ratings rejected")
            
            # Test empty comment
            result = self.rating_system.submit_rating(
                service_id=401,
                customer_id=107,
                provider_id=602,
                rating=4.0,
                comment="",
                category=ServiceCategory.PEST_CONTROL
            )
            
            if result:
                self._record_test("Edge cases - empty comment", True, 
                                 "Empty comment accepted")
            else:
                self._record_test("Edge cases - empty comment", False, 
                                 "Empty comment rejected")
                
        except Exception as e:
            self._record_test("Edge cases", False, f"Exception: {str(e)}")
    
    def _test_data_persistence(self):
        """Test data persistence"""
        print("\n--- Test 7: Data Persistence ---")
        
        try:
            # Save data
            self.rating_system.db.save_data()
            
            # Reload data
            self.rating_system.db._load_data()
            
            # Verify data
            if len(self.rating_system.db.ratings) > 0:
                self._record_test("Data persistence", True, 
                                 f"{len(self.rating_system.db.ratings)} ratings persisted")
            else:
                self._record_test("Data persistence", False, 
                                 "No data found after reload")
                
        except Exception as e:
            self._record_test("Data persistence", False, f"Exception: {str(e)}")
    
    def _test_review_helpfulness(self):
        """Test review helpfulness functionality"""
        print("\n--- Test 8: Review Helpfulness ---")
        
        try:
            # Submit rating and review
            self.rating_system.submit_rating(
                service_id=500,
                customer_id=108,
                provider_id=701,
                rating=4.5,
                comment="Test service",
                category=ServiceCategory.OTHER
            )
            
            self.rating_system.submit_review(
                rating_id=len(self.rating_system.db.ratings),
                reviewer_id=302,
                review_text="This is a test review"
            )
            
            # Mark review as helpful
            result = self.rating_system.mark_review_helpful(1)
            
            if result:
                # Verify helpful count increased
                review = self.rating_system.db.reviews[0]
                if review.helpful_count == 1:
                    self._record_test("Review helpfulness", True, 
                                     "Review marked helpful successfully")
                else:
                    self._record_test("Review helpfulness", False, 
                                     f"Helpful count: {review.helpful_count}, expected 1")
            else:
                self._record_test("Review helpfulness", False, 
                                 "Failed to mark review as helpful")
                
        except Exception as e:
            self._record_test("Review helpfulness", False, f"Exception: {str(e)}")
    
    def _generate_summary(self):
        """Generate test summary report"""
        print("\n" + "="*60)
        print("TEST SUMMARY REPORT")
        print("="*60)
        
        total_tests = len(self.tests_run)
        passed_count = len(self.passed_tests)
        failed_count = len(self.failed_tests)
        pass_rate = (passed_count / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\nTotal Tests Run: {total_tests}")
        print(f"Passed: {passed_count}")
        print(f"Failed: {failed_count}")
        print(f"Pass Rate: {pass_rate:.2f}%")
        
        print("\n" + "-"*60)
        print("DETAILED RESULTS:")
        print("-"*60)
        
        for test_name, result in self.test_results.items():
            status = "✓ PASSED" if result['passed'] else "✗ FAILED"
            print(f"\n{test_name}")
            print(f"  Status: {status}")
            print(f"  Details: {result['details']}")
        
        # Generate summary file
        summary = {
            'test_suite': 'Ratings & Testing Coordinator',
            'run_time': datetime.now().isoformat(),
            'total_tests': total_tests,
            'passed': passed_count,
            'failed': failed_count,
            'pass_rate': pass_rate,
            'test_results': self.test_results
        }
        
        with open('test_report_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        print("\n" + "="*60)
        print(f"Detailed report saved to 'test_report_summary.json'")
        print("="*60)
        
        # Final status
        if failed_count == 0:
            print("\n✅ ALL TESTS PASSED!")
        else:
            print(f"\n⚠️  {failed_count} TEST(S) FAILED - Please review the details above")
    
    def generate_html_report(self):
        """Generate HTML report for better visualization"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Ratings & Testing Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .summary {{ background: #f0f0f0; padding: 15px; border-radius: 5px; }}
                .passed {{ color: green; }}
                .failed {{ color: red; }}
                .test-result {{ margin: 10px 0; padding: 10px; border-left: 3px solid #ccc; }}
                .test-passed {{ border-left-color: green; }}
                .test-failed {{ border-left-color: red; }}
            </style>
        </head>
        <body>
            <h1>Ratings & Testing Coordinator Report</h1>
            <div class="summary">
                <h2>Summary</h2>
                <p>Total Tests: {len(self.tests_run)}</p>
                <p>Passed: <span class="passed">{len(self.passed_tests)}</span></p>
                <p>Failed: <span class="failed">{len(self.failed_tests)}</span></p>
                <p>Pass Rate: {(len(self.passed_tests)/len(self.tests_run)*100):.2f}%</p>
            </div>
            <h2>Test Details</h2>
        """
        
        for test_name, result in self.test_results.items():
            status_class = "test-passed" if result['passed'] else "test-failed"
            status_text = "✓ PASSED" if result['passed'] else "✗ FAILED"
            html_content += f"""
            <div class="test-result {status_class}">
                <h3>{test_name}</h3>
                <p><strong>Status:</strong> {status_text}</p>
                <p><strong>Details:</strong> {result['details']}</p>
                <p><strong>Time:</strong> {result['timestamp']}</p>
            </div>
            """
        
        html_content += """
        </body>
        </html>
        """
        
        with open('test_report.html', 'w') as f:
            f.write(html_content)
        
        print("HTML report generated: test_report.html")

if __name__ == '__main__':
    report = TestingReport()
    report.run_all_tests()
    report.generate_html_report()