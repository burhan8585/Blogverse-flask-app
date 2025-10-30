# 

from app import app, db
from models import Post, Category, Tag, User
from sqlalchemy.sql import func  # For future-proof datetime
from datetime import datetime, timedelta

def seed_database():
    with app.app_context():
        db.create_all()
        
        if Category.query.count() > 0:
            print("Database already seeded! Skipping...")
            return
        
        # Create admin user
        admin = User(username='admin', email='admin@blog.com', is_admin=True)
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("Created admin user: admin / admin123")
        
        # Categories
        categories = [
            Category(name='Technology', slug='technology'),
            Category(name='Design', slug='design'),
            Category(name='Business', slug='business'),
            Category(name='Lifestyle', slug='lifestyle'),
            Category(name='Travel', slug='travel')
        ]
        
        for cat in categories:
            db.session.add(cat)
        
        db.session.commit()
        print(f"Added {len(categories)} categories")
        
        # Tags
        tags_data = [
            ('Web Development', 'web-development'),
            ('Python', 'python'),
            ('JavaScript', 'javascript'),
            ('UI/UX', 'ui-ux'),
            ('Marketing', 'marketing'),
            ('Productivity', 'productivity'),
            ('Startups', 'startups'),
            ('Remote Work', 'remote-work')
        ]
        
        tags = []
        for name, slug in tags_data:
            tag = Tag(name=name, slug=slug)
            db.session.add(tag)
            tags.append(tag)
        
        db.session.commit()
        print(f"Added {len(tags)} tags")
        
        # Posts
        posts_data = [
            {
                'title': 'Building Modern Web Applications with Flask and Bootstrap',
                'slug': 'building-modern-web-apps-flask-bootstrap',
                'content': '''<p>Flask is a lightweight Python web framework that makes it easy to build modern web applications. Combined with Bootstrap, you can create beautiful, responsive interfaces quickly.</p>

<h2>Why Flask?</h2>
<p>Flask provides the perfect balance of simplicity and power. Its minimalist approach means you only include what you need, keeping your application lean and maintainable.</p>

<h2>Bootstrap for Beautiful UIs</h2>
<p>Bootstrap 5 brings modern design patterns and components that work seamlessly across all devices. The combination of Flask's backend capabilities and Bootstrap's frontend polish creates exceptional user experiences.</p>

<p>Whether you're building a blog, e-commerce site, or complex web application, Flask and Bootstrap provide the foundation for success.</p>''',
                'excerpt': 'Discover how Flask and Bootstrap combine to create modern, beautiful web applications with clean code and responsive design.',
                'author': 'Sarah Johnson',
                'image_url': 'https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=800&q=80',
                'category': 'Technology',
                'tags': ['Web Development', 'Python'],
                'featured': True,
                'published': True
            },
            {
                'title': 'The Art of Clean UI Design: Principles and Best Practices',
                'slug': 'art-of-clean-ui-design',
                'content': '''<p>Clean UI design is about removing unnecessary elements and focusing on what matters. It's the art of simplicity that creates powerful user experiences.</p>

<h2>Core Principles</h2>
<p>Start with plenty of white space. Give your content room to breathe. Use consistent spacing, clear typography, and a limited color palette to create visual harmony.</p>

<h2>User-Centered Approach</h2>
<p>Every design decision should serve the user's needs. Ask yourself: does this element help users accomplish their goals? If not, remove it.</p>

<p>Clean design isn't about minimalism for its own sake—it's about clarity, focus, and creating interfaces that feel effortless to use.</p>''',
                'excerpt': 'Learn the principles of clean UI design that create beautiful, user-friendly interfaces with maximum impact.',
                'author': 'Michael Chen',
                'image_url': 'https://images.unsplash.com/photo-1561070791-2526d30994b5?w=800&q=80',
                'category': 'Design',
                'tags': ['UI/UX', 'Web Development'],
                'featured': True,
                'published': True
            },
            {
                'title': 'Scaling Your Startup: Lessons from the Trenches',
                'slug': 'scaling-your-startup-lessons',
                'content': '''<p>Scaling a startup is one of the most challenging phases of building a business. Here are hard-won lessons from founders who've been there.</p>

<h2>Hire Slow, Fire Fast</h2>
<p>Your early team will define your company culture. Take time to find people who share your vision and values. But don't hesitate to make changes when someone isn't working out.</p>

<h2>Focus on Unit Economics</h2>
<p>Before you scale, make sure your business model works at a small scale. You can't scale your way out of a broken business model.</p>

<p>Growth is exciting, but sustainable growth built on solid fundamentals is what creates lasting success.</p>''',
                'excerpt': 'Real-world lessons on scaling startups from founders who have successfully navigated the journey.',
                'author': 'David Martinez',
                'image_url': 'https://images.unsplash.com/photo-1559136555-9303baea8ebd?w=800&q=80',
                'category': 'Business',
                'tags': ['Startups', 'Marketing'],
                'featured': True,
                'published': True
            },
            {
                'title': 'Mastering Productivity: My Daily Routine for Peak Performance',
                'slug': 'mastering-productivity-daily-routine',
                'content': '''<p>After years of experimentation, I've found a daily routine that maximizes my productivity while maintaining work-life balance.</p>

<h2>Morning Rituals</h2>
<p>I start each day with 30 minutes of exercise and meditation. This sets a positive tone and gives me mental clarity for the day ahead.</p>

<h2>Deep Work Blocks</h2>
<p>I schedule 2-3 hours of uninterrupted focus time each morning for my most important work. No meetings, no email—just deep, focused work.</p>

<p>Productivity isn't about working more hours—it's about making your hours count.</p>''',
                'excerpt': 'A proven daily routine that helps you achieve peak productivity while maintaining balance and well-being.',
                'author': 'Emily Watson',
                'image_url': 'https://images.unsplash.com/photo-1484480974693-6ca0a78fb36b?w=800&q=80',
                'category': 'Lifestyle',
                'tags': ['Productivity', 'Remote Work'],
                'featured': False,
                'published': True
            },
            {
                'title': 'Hidden Gems: 10 Off-the-Beaten-Path Destinations in Europe',
                'slug': 'hidden-gems-europe-destinations',
                'content': '''<p>Tired of tourist crowds? These lesser-known European destinations offer authentic experiences and breathtaking beauty.</p>

<h2>Slovenia's Lake Bohinj</h2>
<p>While everyone flocks to Lake Bled, Lake Bohinj offers similar beauty with a fraction of the tourists. Crystal-clear waters surrounded by Julian Alps create a perfect retreat.</p>

<h2>Porto, Portugal</h2>
<p>While Lisbon gets all the attention, Porto charms with its colorful riverside, port wine cellars, and authentic Portuguese culture.</p>

<p>These hidden gems remind us that the best travel experiences often come from exploring beyond the guidebook.</p>''',
                'excerpt': 'Discover stunning European destinations that offer authentic experiences away from the tourist crowds.',
                'author': 'Alex Rivera',
                'image_url': 'https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=800&q=80',
                'category': 'Travel',
                'tags': ['Remote Work'],
                'featured': False,
                'published': True
            },
            {
                'title': 'JavaScript ES2024: New Features You Should Know',
                'slug': 'javascript-es2024-new-features',
                'content': '''<p>JavaScript continues to evolve with exciting new features in ES2024 that make development more elegant and efficient.</p>

<h2>Array Grouping</h2>
<p>The new Object.groupBy() method makes it trivial to group array elements by any criteria, eliminating the need for complex reduce operations.</p>

<h2>Pipeline Operator</h2>
<p>The pipeline operator brings functional programming elegance to JavaScript, making chained operations more readable.</p>

<p>These features show JavaScript's commitment to developer experience and modern programming patterns.</p>''',
                'excerpt': 'Explore the latest JavaScript features in ES2024 that will improve your code quality and developer experience.',
                'author': 'Sarah Johnson',
                'image_url': 'https://images.unsplash.com/photo-1579468118864-1b9ea3c0db4a?w=800&q=80',
                'category': 'Technology',
                'tags': ['JavaScript', 'Web Development'],
                'featured': False,
                'published': True
            },
            {
                'title': 'Creating a Design System: A Complete Guide',
                'slug': 'creating-design-system-guide',
                'content': '''<p>A design system is more than a style guide—it's a comprehensive collection of reusable components, patterns, and guidelines.</p>

<h2>Starting with Foundations</h2>
<p>Begin with color palettes, typography scales, and spacing systems. These foundational elements ensure consistency across all designs.</p>

<h2>Building Components</h2>
<p>Document each component with usage guidelines, accessibility considerations, and code examples.</p>

<p>A well-crafted design system accelerates development and ensures consistent user experiences.</p>''',
                'excerpt': 'A comprehensive guide to building design systems that scale with your product and team.',
                'author': 'Michael Chen',
                'image_url': 'https://images.unsplash.com/photo-1507238691740-187a5b1d37b8?w=800&q=80',
                'category': 'Design',
                'tags': ['UI/UX', 'Web Development'],
                'featured': False,
                'published': True
            },
            {
                'title': 'Remote Work Revolution: Building Distributed Teams',
                'slug': 'remote-work-distributed-teams',
                'content': '''<p>Remote work isn't just a trend—it's reshaping how we build and manage teams. Here's how to make it work.</p>

<h2>Communication is Key</h2>
<p>Overcommunicate deliberately. What was once a quick desk chat now requires intentional communication channels and practices.</p>

<h2>Trust and Autonomy</h2>
<p>Remote work demands trust. Focus on outcomes, not hours. Give team members autonomy and they'll reward you with their best work.</p>

<p>The future of work is distributed, and companies that adapt will attract the best talent.</p>''',
                'excerpt': 'Learn how to build and manage successful distributed teams in the remote work era.',
                'author': 'David Martinez',
                'image_url': 'https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=800&q=80',
                'category': 'Business',
                'tags': ['Remote Work', 'Productivity'],
                'featured': False,
                'published': True
            },
            {
                'title': 'Mindful Living: Finding Balance in a Busy World',
                'slug': 'mindful-living-finding-balance',
                'content': '''<p>In our always-on world, mindfulness offers a path to peace, focus, and authentic living.</p>

<h2>Present Moment Awareness</h2>
<p>Mindfulness starts with paying attention to the present moment without judgment. It's simple but not easy.</p>

<h2>Daily Practice</h2>
<p>Start with just five minutes of meditation each morning. Gradually increase as the habit forms. Consistency matters more than duration.</p>

<p>Mindfulness isn't about eliminating stress—it's about changing your relationship with it.</p>''',
                'excerpt': 'Discover how mindfulness practices can help you find balance and peace in everyday life.',
                'author': 'Emily Watson',
                'image_url': 'https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=800&q=80',
                'category': 'Lifestyle',
                'tags': ['Productivity'],
                'featured': False,
                'published': True
            }
        ]
        
        for i, post_data in enumerate(posts_data):
            category = Category.query.filter_by(name=post_data['category']).first()
            if not category:
                print(f"Warning: Category '{post_data['category']}' not found for post '{post_data['title']}'")
                continue
            
            post = Post(
                title=post_data['title'],
                slug=post_data['slug'],
                content=post_data['content'],
                excerpt=post_data['excerpt'],
                author=post_data['author'],
                image_url=post_data['image_url'],
                category_id=category.id,  # FIXED: Use category_id, not category
                featured=post_data['featured'],
                published=post_data['published'],
                created_at=func.now() - timedelta(days=len(posts_data) - i)  # FIXED: Use func.now() for UTC
            )
            
            for tag_name in post_data['tags']:
                tag = Tag.query.filter_by(name=tag_name).first()
                if tag:
                    post.tags.append(tag)
                else:
                    print(f"Warning: Tag '{tag_name}' not found for post '{post_data['title']}'")
            
            db.session.add(post)
        
        db.session.commit()
        print(f"Added {len(posts_data)} posts")
        print("Database seeded successfully! Run 'python app.py' to start the server.")

if __name__ == '__main__':
    try:
        seed_database()
    except Exception as e:
        print(f"Seeding failed: {e}")
        db.session.rollback()  # Rollback on error