# main.py
from rating_system import RatingSystem
from testing_report import TestingReport
from debugger import RatingDebugger
from models import ServiceCategory
from utils import Utils
import sys

def main():
    print("="*60)
    print("LOCAL AREA SERVICE OPERATOR - RATING SYSTEM")
    print("="*60)
    
    # Initialize components
    rating_system = RatingSystem()
    debugger = RatingDebugger()
    
    while True:
        print("\nMAIN MENU")
        print("-"*60)
        print("1. Submit Rating")
        print("2. Submit Review")
        print("3. View Provider Statistics")
        print("4. View Category Averages")
        print("5. View Customer Ratings")
        print("6. Run Test Suite")
        print("7. View Debug Report")
        print("8. Exit")
        print("-"*60)
        
        choice = input("Enter your choice (1-8): ")
        
        if choice == '1':
            submit_rating(rating_system, debugger)
        elif choice == '2':
            submit_review(rating_system, debugger)
        elif choice == '3':
            view_provider_stats(rating_system, debugger)
        elif choice == '4':
            view_category_averages(rating_system)
        elif choice == '5':
            view_customer_ratings(rating_system)
        elif choice == '6':
            run_tests()
        elif choice == '7':
            view_debug_report(debugger)
        elif choice == '8':
            print("\nExiting system. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

def submit_rating(rating_system, debugger):
    """Submit a rating"""
    print("\n--- Submit Rating ---")
    
    try:
        service_id = int(input("Service ID: "))
        customer_id = int(input("Customer ID: "))
        provider_id = int(input("Provider ID: "))
        rating = float(input("Rating (1.0 - 5.0): "))
        comment = input("Comment: ")
        
        print("\nCategories:")
        for category in ServiceCategory:
            print(f"  {category.value}")
        
        category_input = input("Category: ")
        category = next((c for c in ServiceCategory if c.value == category_input), None)
        
        if category is None:
            print("Invalid category!")
            return
        
        rating_data = {
            'service_id': service_id,
            'customer_id': customer_id,
            'provider_id': provider_id,
            'rating': rating,
            'category': category_input,
            'comment': comment
        }
        
        debugger.debug_rating_submission(rating_data)
        
        success = rating_system.submit_rating(
            service_id=service_id,
            customer_id=customer_id,
            provider_id=provider_id,
            rating=rating,
            comment=comment,
            category=category
        )
        
        if success:
            print("✓ Rating submitted successfully!")
        else:
            print("✗ Failed to submit rating!")
            
    except ValueError as e:
        print(f"Error: {e}")

def submit_review(rating_system, debugger):
    """Submit a review"""
    print("\n--- Submit Review ---")
    
    try:
        rating_id = int(input("Rating ID: "))
        reviewer_id = int(input("Reviewer ID: "))
        review_text = input("Review Text: ")
        is_verified = input("Is Verified? (y/n): ").lower() == 'y'
        
        review_data = {
            'rating_id': rating_id,
            'reviewer_id': reviewer_id,
            'review_text': review_text
        }
        
        debugger.debug_review_submission(review_data)
        
        success = rating_system.submit_review(
            rating_id=rating_id,
            reviewer_id=reviewer_id,
            review_text=review_text,
            is_verified=is_verified
        )
        
        if success:
            print("✓ Review submitted successfully!")
        else:
            print("✗ Failed to submit review!")
            
    except ValueError as e:
        print(f"Error: {e}")

def view_provider_stats(rating_system, debugger):
    """View provider statistics"""
    print("\n--- Provider Statistics ---")
    
    try:
        provider_id = int(input("Provider ID: "))
        stats = rating_system.get_provider_stats(provider_id)
        
        debugger.debug_provider_stats(provider_id, stats)
        
        print("\n" + "-"*60)
        print(Utils.generate_summary(stats))
        print("-"*60)
        
    except ValueError as e:
        print(f"Error: {e}")

def view_category_averages(rating_system):
    """View category averages"""
    print("\n--- Category Averages ---")
    
    print("\n" + "-"*60)
    for category in ServiceCategory:
        avg = rating_system.get_category_average(category)
        print(f"{category.value:15}: {Utils.format_rating(avg)}")
    print("-"*60)

def view_customer_ratings(rating_system):
    """View customer ratings"""
    print("\n--- Customer Ratings ---")
    
    try:
        customer_id = int(input("Customer ID: "))
        ratings = rating_system.get_customer_ratings(customer_id)
        
        if not ratings:
            print("No ratings found for this customer.")
            return
        
        print("\n" + "-"*60)
        for rating in ratings:
            print(f"Service {rating.service_id}: {Utils.format_rating(rating.rating)} - {rating.comment}")
            print(f"  Provider: {rating.provider_id}, Category: {rating.category.value}")
            print(f"  Date: {rating.timestamp.strftime('%Y-%m-%d %H:%M')}")
            print("-"*60)
            
    except ValueError as e:
        print(f"Error: {e}")

def run_tests():
    """Run test suite"""
    print("\n--- Running Test Suite ---")
    test_report = TestingReport()
    test_report.run_all_tests()
    test_report.generate_html_report()

def view_debug_report(debugger):
    """View debug report"""
    print("\n--- Debug Report ---")
    report = debugger.get_debug_report()
    
    print("\n" + "-"*60)
    print(f"Total Messages: {report['total_messages']}")
    print(f"Errors: {report['error_count']}")
    print(f"Warnings: {report['warning_count']}")
    print(f"Error Rate: {report['error_rate']:.2f}%")
    print("-"*60)
    
    if report['errors']:
        print("\nRecent Errors:")
        for error in report['errors'][-5:]:
            print(f"  {error['timestamp']}: {error['message']}")
            if error.get('error'):
                print(f"    {error['error']}")
    
    if report['warnings']:
        print("\nRecent Warnings:")
        for warning in report['warnings'][-5:]:
            print(f"  {warning['timestamp']}: {warning['message']}")

if __name__ == '__main__':
    main()