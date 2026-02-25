from flask import Flask, jsonify, request, render_template, redirect, url_for, session
from flask_cors import CORS
from models import db, Temple, Prasadam, Order, User, Payment
from datetime import datetime
import os
import uuid
import hashlib
import jwt
from functools import wraps

app = Flask(__name__, 
            static_folder='static',
            template_folder='templates')

# Configuration - Make sure these are set BEFORE initializing db
app.config['SECRET_KEY'] = 'e-prashadam-secret-key-2024'
app.config['JWT_SECRET_KEY'] = 'e-prashadam-jwt-secret-2024'

# Database configuration - Use absolute path
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'eprashadam.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Session configuration
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_PERMANENT'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = 3600

# Payment configuration
app.config['PAYMENT_MODE'] = 'TEST'
app.config['RAZORPAY_KEY_ID'] = 'rzp_test_YourTestKeyHere'
app.config['RAZORPAY_KEY_SECRET'] = 'YourTestSecretHere'

# Initialize CORS
CORS(app, supports_credentials=True, origins=["http://localhost:5000"])

# Initialize database - This must come AFTER configuration
db.init_app(app)

# Create instance folder if it doesn't exist
instance_path = os.path.join(basedir, 'instance')
if not os.path.exists(instance_path):
    os.makedirs(instance_path)

# Authentication decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(" ")[1]
        
        if not token and 'token' in session:
            token = session['token']
        
        if not token:
            return jsonify({'success': False, 'message': 'Token is missing!'}), 401
        
        try:
            data = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.get(data['user_id'])
            
            if not current_user:
                return jsonify({'success': False, 'message': 'User not found!'}), 401
                
        except jwt.ExpiredSignatureError:
            return jsonify({'success': False, 'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'success': False, 'message': 'Invalid token!'}), 401
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def seed_database():
    """Seed the database with initial data"""
    print("Seeding database...")
    
    # Check if tables exist and have data
    if Temple.query.count() > 0:
        print("Database already has data, skipping seed")
        return
    
    # 12 Jyotirlingas with descriptions
    jyotirlingas = [
        {
            'name': 'Somnath Temple',
            'location': 'Gujarat',
            'type': 'jyotirlinga',
            'description': 'The first among the twelve Jyotirlingas',
            'prasadam': ['Sugarcane Prasad', 'Panchamrut', 'Laddu']
        },
        {
            'name': 'Mallikarjuna Temple',
            'location': 'Andhra Pradesh',
            'type': 'jyotirlinga',
            'description': 'Situated on Shri Shaila Mountain',
            'prasadam': ['Pongal', 'Pulihora', 'Laddu']
        },
        {
            'name': 'Mahakaleshwar Temple',
            'location': 'Ujjain, Madhya Pradesh',
            'type': 'jyotirlinga',
            'description': 'Known for its Bhasma Aarti',
            'prasadam': ['Mahaprasad', 'Panchamrut', 'Kheel']
        },
        {
            'name': 'Omkareshwar Temple',
            'location': 'Madhya Pradesh',
            'type': 'jyotirlinga',
            'description': 'Situated on an island in Narmada river',
            'prasadam': ['Narmada Jal', 'Panchamrut', 'Besan Laddu']
        },
        {
            'name': 'Kedarnath Temple',
            'location': 'Uttarakhand',
            'type': 'jyotirlinga',
            'description': 'Located in the Himalayas',
            'prasadam': ['Charnamrit', 'Dry Fruits', 'Panchamrut']
        },
        {
            'name': 'Bhimashankar Temple',
            'location': 'Maharashtra',
            'type': 'jyotirlinga',
            'description': 'Located in Sahyadri hills',
            'prasadam': ['Puran Poli', 'Panchamrut', 'Laddu']
        },
        {
            'name': 'Kashi Vishwanath Temple',
            'location': 'Varanasi, Uttar Pradesh',
            'type': 'jyotirlinga',
            'description': 'Most famous Jyotirlinga',
            'prasadam': ['Ganga Jal', 'Panchamrut', 'Laddu']
        },
        {
            'name': 'Trimbakeshwar Temple',
            'location': 'Nashik, Maharashtra',
            'type': 'jyotirlinga',
            'description': 'Source of Godavari river',
            'prasadam': ['Godavari Jal', 'Panchamrut', 'Pedha']
        },
        {
            'name': 'Vaidyanath Temple',
            'location': 'Deoghar, Jharkhand',
            'type': 'jyotirlinga',
            'description': 'One of the 51 Shakti Peethas',
            'prasadam': ['Bael Patra', 'Panchamrut', 'Laddu']
        },
        {
            'name': 'Nageshwar Temple',
            'location': 'Gujarat',
            'type': 'jyotirlinga',
            'description': 'Dwarka Shiva Temple',
            'prasadam': ['Tulsi Prasad', 'Panchamrut', 'Dry Fruits']
        },
        {
            'name': 'Rameshwaram Temple',
            'location': 'Tamil Nadu',
            'type': 'jyotirlinga',
            'description': 'Southernmost Jyotirlinga',
            'prasadam': ['Sandalwood Paste', 'Panchamrut', 'Pongal']
        },
        {
            'name': 'Grishneshwar Temple',
            'location': 'Aurangabad, Maharashtra',
            'type': 'jyotirlinga',
            'description': 'Last of the twelve Jyotirlingas',
            'prasadam': ['Shiva Linga Abhishek Kit', 'Panchamrut', 'Laddu']
        }
    ]
    
    # Major Dhams
    dhams = [
        {
            'name': 'Badrinath Dham',
            'location': 'Uttarakhand',
            'type': 'dham',
            'description': 'Abode of Lord Vishnu',
            'prasadam': ['Badri Tulsi', 'Dry Fruits', 'Panchamrut']
        },
        {
            'name': 'Dwarka Dham',
            'location': 'Gujarat',
            'type': 'dham',
            'description': 'Kingdom of Lord Krishna',
            'prasadam': ['Dwarka Prasad', 'Panchamrut', 'Maha Prasad']
        },
        {
            'name': 'Jagannath Puri Dham',
            'location': 'Odisha',
            'type': 'dham',
            'description': 'Famous for Rath Yatra',
            'prasadam': ['Mahaprasad', 'Khaja', 'Peda']
        },
        {
            'name': 'Rameshwaram Dham',
            'location': 'Tamil Nadu',
            'type': 'dham',
            'description': 'Southern pilgrimage site',
            'prasadam': ['Sandalwood Paste', 'Pongal', 'Laddu']
        }
    ]
    
    try:
        # Add temples to database
        for temple_data in jyotirlingas + dhams:
            temple = Temple(
                name=temple_data['name'],
                location=temple_data['location'],
                type=temple_data['type'],
                description=temple_data['description']
            )
            db.session.add(temple)
            db.session.flush()  # Get the temple ID
            
            # Add prasadam items
            for prasad_item in temple_data['prasadam']:
                prasadam = Prasadam(
                    temple_id=temple.id,
                    name=prasad_item,
                    description=f"Blessed prasadam from {temple.name}",
                    price=150.0 + len(prasad_item) * 10,
                    available=True
                )
                db.session.add(prasadam)
        
        # Create a demo user if no users exist
        if User.query.count() == 0:
            demo_user = User(
                name="Demo Devotee",
                email="devotee@example.com",
                phone="9876543210",
                password_hash=hash_password("prasadam123"),
                address="Varanasi, Uttar Pradesh"
            )
            db.session.add(demo_user)
            print("Demo user created: devotee@example.com / prasadam123")
        
        db.session.commit()
        print("Database seeded successfully!")
        
    except Exception as e:
        db.session.rollback()
        print(f"Error seeding database: {e}")
        raise e

# Create tables and seed data
with app.app_context():
    try:
        print("Creating database tables...")
        db.create_all()
        print("Database tables created successfully!")
        
        print("Checking if database needs seeding...")
        seed_database()
        
    except Exception as e:
        print(f"Error during database initialization: {e}")
        raise e

# Routes
@app.route('/')
def home():
    """Root route - redirect based on login status"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login_page'))

@app.route('/login')
def login_page():
    """Serve login/signup page"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('auth.html')

@app.route('/signup')
def signup_page():
    """Serve signup page - redirect to login with signup hash"""
    return redirect(url_for('login_page', _anchor='signup'))

@app.route('/dashboard')
def dashboard():
    """Serve main dashboard after login"""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('index.html')

@app.route('/logout')
def logout_route():
    """Logout and redirect to login"""
    session.clear()
    return redirect(url_for('login_page'))

# Authentication API Endpoints
@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['name', 'email', 'phone', 'password']
        for field in required_fields:
            if field not in data or not data[field].strip():
                return jsonify({'success': False, 'message': f'{field} is required'}), 400
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({'success': False, 'message': 'User already exists'}), 400
        
        # Create new user
        new_user = User(
            name=data['name'],
            email=data['email'],
            phone=data['phone'],
            password_hash=hash_password(data['password']),
            address=data.get('address', ''),
            is_active=True
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        # Generate JWT token
        token = jwt.encode({
            'user_id': new_user.id,
            'email': new_user.email,
            'exp': datetime.utcnow().timestamp() + 86400
        }, app.config['JWT_SECRET_KEY'], algorithm="HS256")
        
        return jsonify({
            'success': True,
            'message': 'Registration successful',
            'user': {
                'id': new_user.id,
                'name': new_user.name,
                'email': new_user.email,
                'phone': new_user.phone
            },
            'token': token
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login"""
    try:
        data = request.json
        
        # Validate required fields
        if 'email' not in data or 'password' not in data:
            return jsonify({'success': False, 'message': 'Email and password are required'}), 400
        
        # Find user by email
        user = User.query.filter_by(email=data['email']).first()
        
        if not user:
            return jsonify({'success': False, 'message': 'Invalid email or password'}), 401
        
        # Verify password
        if user.password_hash != hash_password(data['password']):
            return jsonify({'success': False, 'message': 'Invalid email or password'}), 401
        
        # Check if user is active
        if not user.is_active:
            return jsonify({'success': False, 'message': 'Account is disabled'}), 403
        
        # Generate JWT token
        token = jwt.encode({
            'user_id': user.id,
            'email': user.email,
            'exp': datetime.utcnow().timestamp() + 86400
        }, app.config['JWT_SECRET_KEY'], algorithm="HS256")
        
        # Store in session
        session['user_id'] = user.id
        session['user_email'] = user.email
        session['user_name'] = user.name
        session['token'] = token
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'phone': user.phone,
                'address': user.address
            },
            'token': token
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """User logout"""
    try:
        session.clear()
        return jsonify({'success': True, 'message': 'Logged out successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/auth/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    """Get current user info"""
    return jsonify({
        'success': True,
        'user': {
            'id': current_user.id,
            'name': current_user.name,
            'email': current_user.email,
            'phone': current_user.phone,
            'address': current_user.address,
            'created_at': current_user.created_at.strftime('%Y-%m-%d %H:%M:%S') if current_user.created_at else None
        }
    })

# Protected API Endpoints
@app.route('/api/temples', methods=['GET'])
@token_required
def get_temples(current_user):
    """Get all temples (protected)"""
    temples = Temple.query.all()
    return jsonify([{
        'id': t.id,
        'name': t.name,
        'location': t.location,
        'type': t.type,
        'description': t.description
    } for t in temples])

@app.route('/api/prasadam', methods=['GET'])
@token_required
def get_all_prasadam(current_user):
    """Get all available prasadam items (protected)"""
    prasadam_items = Prasadam.query.filter_by(available=True).all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'description': p.description,
        'price': p.price,
        'temple_name': Temple.query.get(p.temple_id).name,
        'temple_type': Temple.query.get(p.temple_id).type
    } for p in prasadam_items])

@app.route('/api/create-order', methods=['POST'])
@token_required
def create_order_with_payment(current_user):
    """Create a new order with payment initiation (protected)"""
    try:
        data = request.json
        
        # Generate unique order ID
        order_id = str(uuid.uuid4())[:8].upper()
        
        # Create order record with user_id
        order = Order(
            order_id=order_id,
            user_id=current_user.id,
            user_name=data['user_name'],
            user_email=data['user_email'],
            user_phone=data['user_phone'],
            user_address=data['user_address'],
            items=data['items'],
            total_amount=data['total_amount'],
            status='payment_pending'
        )
        db.session.add(order)
        db.session.commit()
        
        # Create payment record
        payment = Payment(
            order_id=order.id,
            payment_order_id=order_id + '_PAY',
            amount=data['total_amount'],
            currency='INR',
            status='pending'
        )
        db.session.add(payment)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Order created. Proceed to payment.',
            'order_id': order.id,
            'payment_order_id': payment.payment_order_id
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/verify-payment', methods=['POST'])
@token_required
def verify_payment(current_user):
    """Verify payment success (protected)"""
    try:
        data = request.json
        
        payment = Payment.query.filter_by(payment_order_id=data['payment_order_id']).first()
        
        if payment:
            # Check if order belongs to current user
            order = Order.query.get(payment.order_id)
            if order.user_id != current_user.id:
                return jsonify({'success': False, 'message': 'Unauthorized access'}), 403
            
            payment.status = 'completed'
            payment.payment_id = data.get('payment_id', 'demo_payment_' + str(uuid.uuid4())[:8])
            payment.payment_method = data.get('payment_method', 'card')
            
            # Update order status
            order.status = 'confirmed'
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Payment verified successfully!',
                'order_id': order.id,
                'payment_id': payment.payment_id
            })
        
        return jsonify({'success': False, 'message': 'Payment not found'}), 404
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/my-orders', methods=['GET'])
@token_required
def get_my_orders(current_user):
    """Get orders for current user (protected)"""
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    
    order_list = []
    for o in orders:
        payment = Payment.query.filter_by(order_id=o.id).first()
        order_list.append({
            'id': o.id,
            'order_id': o.order_id,
            'user_name': o.user_name,
            'user_email': o.user_email,
            'items': o.items,
            'total_amount': o.total_amount,
            'status': o.status,
            'payment_status': payment.status if payment else 'N/A',
            'created_at': o.created_at.strftime('%Y-%m-%d %H:%M:%S') if o.created_at else None
        })
    
    return jsonify(order_list)

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'E-Prashadam API',
        'version': '1.0.0',
        'timestamp': datetime.utcnow().isoformat()
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'message': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'message': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)