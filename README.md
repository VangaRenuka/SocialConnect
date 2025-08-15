# SocialConnect - Social Media Backend Application

A comprehensive social media backend application built with Django REST Framework, featuring user authentication, content management, real-time notifications, and personalized feeds.

## 🚀 Features

### Core Functionality
- **User Authentication System**: JWT-based authentication with comprehensive user management
- **User Profiles**: Rich profiles with bio, avatar, follower/following counts, and privacy controls
- **Content Creation**: Text posts with image upload support and categories
- **Social Interactions**: Follow/unfollow users, like posts, and comment system
- **Personalized Feeds**: Chronological feeds from followed users with filtering options
- **Real-time Notifications**: Live notifications using WebSocket technology
- **Admin Panel**: Comprehensive user and content management for administrators

### Technical Features
- **RESTful API**: Well-structured API endpoints following REST principles
- **JWT Authentication**: Secure token-based authentication system
- **Database Optimization**: Efficient queries with proper indexing and select_related
- **File Upload**: Image upload support with validation and storage
- **Real-time Communication**: WebSocket support for live notifications
- **Role-based Access Control**: Different permission levels for users and admins

## 🛠️ Technology Stack

- **Backend**: Django 4.2.7, Django REST Framework 3.14.0
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Database**: PostgreSQL
- **Real-time**: Django Channels with WebSocket support
- **File Storage**: Supabase Storage (configurable)
- **Cache**: Redis
- **Task Queue**: Celery (for background tasks)

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL
- Redis
- Virtual environment (recommended)

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd SocialConnect
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env file with your configuration
   ```

5. **Set up database**
   ```bash
   # Create PostgreSQL database
   createdb socialconnect
   
   # Run migrations
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

## 🗄️ Database Models

### User Management
- **User**: Extended user model with profile fields, roles, and privacy settings
- **Follow**: Follow relationships between users

### Content Management
- **Post**: User posts with content, images, categories, and engagement metrics
- **Comment**: Comments on posts with nested structure support
- **Like**: Post likes with automatic count updates
- **PostImage**: Image management for posts

### Notifications
- **Notification**: Real-time notifications for various events
- **NotificationPreference**: User preferences for notification types and methods

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `POST /api/auth/password/change/` - Change password
- `POST /api/auth/password/reset/` - Request password reset
- `POST /api/auth/password/reset/confirm/` - Confirm password reset

### User Management
- `GET /api/users/me/` - Get current user profile
- `PUT /api/users/me/` - Update current user profile
- `GET /api/users/<username>/` - Get user profile by username
- `GET /api/users/` - List users (with search and filtering)
- `POST /api/users/<user_id>/follow/` - Follow user
- `DELETE /api/users/<user_id>/follow/` - Unfollow user
- `GET /api/users/<user_id>/followers/` - Get user followers
- `GET /api/users/<user_id>/following/` - Get users being followed

### Posts
- `GET /api/posts/` - List all posts
- `POST /api/posts/create/` - Create new post
- `GET /api/posts/<id>/` - Get post details
- `PUT /api/posts/<id>/` - Update post
- `DELETE /api/posts/<id>/` - Delete post
- `POST /api/posts/<id>/like/` - Like post
- `DELETE /api/posts/<id>/unlike/` - Unlike post
- `GET /api/posts/<id>/like-status/` - Check like status

### Comments
- `GET /api/posts/<post_id>/comments/` - List post comments
- `POST /api/posts/<post_id>/comments/create/` - Create comment
- `GET /api/posts/comments/<id>/` - Get comment details
- `PUT /api/posts/comments/<id>/` - Update comment
- `DELETE /api/posts/comments/<id>/` - Delete comment

### Feed
- `GET /api/feed/` - Personalized feed
- `GET /api/feed/trending/` - Trending posts
- `GET /api/feed/category/<category>/` - Category-specific feed

### Notifications
- `GET /api/notifications/` - List user notifications
- `GET /api/notifications/<id>/` - Get notification details
- `POST /api/notifications/<id>/read/` - Mark notification as read
- `POST /api/notifications/mark-all-read/` - Mark all notifications as read
- `POST /api/notifications/<id>/archive/` - Archive notification
- `GET /api/notifications/stats/` - Notification statistics
- `GET /api/notifications/preferences/` - Get notification preferences
- `PUT /api/notifications/preferences/` - Update notification preferences

### Admin Endpoints
- `GET /api/admin/users/` - List all users (admin only)
- `GET /api/admin/users/<id>/` - Get user details (admin only)
- `POST /api/admin/users/<id>/deactivate/` - Deactivate user (admin only)
- `GET /api/admin/stats/` - System statistics (admin only)
- `GET /api/admin/posts/` - List all posts (admin only)
- `DELETE /api/admin/posts/<id>/delete/` - Delete any post (admin only)

## 🔐 Authentication & Permissions

### User Roles
- **User**: Default role with basic social media functionality
- **Admin**: Elevated privileges for user and content management

### Permission System
- Users can only edit their own content
- Admins can manage all users and content
- Profile visibility controls (public, private, followers-only)
- Content moderation capabilities

## 🔄 Real-time Features

### WebSocket Notifications
- Live notifications for follows, likes, and comments
- User-specific notification channels
- Automatic notification creation via Django signals

### Notification Types
- **Follow**: New follower notifications
- **Like**: Post like notifications
- **Comment**: Comment on user's post
- **Mention**: User mentions in comments
- **System**: System-wide announcements

## 📱 Frontend Integration

The backend is designed to work seamlessly with modern frontend frameworks:

- **React/Next.js**: Full API support with TypeScript
- **Mobile Apps**: RESTful API endpoints for mobile applications
- **WebSocket**: Real-time features for web applications

## 🚀 Deployment

### Production Setup
1. Set `DEBUG=False` in environment variables
2. Configure production database
3. Set up Redis for production
4. Configure static file serving
5. Set up SSL certificates
6. Configure email settings

### Docker Support
```bash
# Build and run with Docker Compose
docker-compose up --build
```

## 🧪 Testing

```bash
# Run tests
python manage.py test

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

## 📊 Performance Optimization

- Database query optimization with select_related and prefetch_related
- Efficient pagination for large datasets
- Redis caching for frequently accessed data
- Background task processing with Celery

## 🔒 Security Features

- JWT token authentication
- Password validation and hashing
- CORS configuration
- Input validation and sanitization
- Role-based access control
- Secure file upload handling

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the API endpoints

## 🎯 Roadmap

- [ ] Advanced search functionality
- [ ] Content recommendation system
- [ ] Analytics and insights
- [ ] Mobile app API optimization
- [ ] Advanced moderation tools
- [ ] Content scheduling
- [ ] API rate limiting
- [ ] Webhook support

---

**SocialConnect** - Building meaningful connections through technology.


