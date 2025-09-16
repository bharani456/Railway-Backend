// MongoDB initialization script

// Switch to the application database
db = db.getSiblingDB('qr_track_fittings');

// Create application user
db.createUser({
  user: 'app_user',
  pwd: 'app_password',
  roles: [
    {
      role: 'readWrite',
      db: 'qr_track_fittings'
    }
  ]
});

// Create collections with initial data
db.createCollection('users');
db.createCollection('zones');
db.createCollection('divisions');
db.createCollection('stations');
db.createCollection('vendors');
db.createCollection('manufacturers');
db.createCollection('fitting_categories');
db.createCollection('fitting_types');
db.createCollection('supply_orders');
db.createCollection('fitting_batches');
db.createCollection('qr_codes');
db.createCollection('fitting_installations');
db.createCollection('inspections');
db.createCollection('maintenance_records');
db.createCollection('qr_scan_logs');
db.createCollection('ai_analysis_reports');
db.createCollection('portal_integrations');
db.createCollection('user_sessions');
db.createCollection('audit_logs');
db.createCollection('notifications');

// Create initial admin user
db.users.insertOne({
  name: "System Administrator",
  email: "admin@qr-track-fittings.com",
  passwordHash: "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.sK2", // password123
  role: "super_admin",
  isActive: true,
  createdAt: new Date(),
  updatedAt: new Date(),
  status: "active"
});

// Create initial zones
db.zones.insertMany([
  {
    name: "Southern Railway",
    code: "SR",
    description: "Southern Railway Zone",
    headquarters: "Chennai",
    createdAt: new Date(),
    updatedAt: new Date(),
    status: "active"
  },
  {
    name: "Northern Railway",
    code: "NR",
    description: "Northern Railway Zone",
    headquarters: "New Delhi",
    createdAt: new Date(),
    updatedAt: new Date(),
    status: "active"
  },
  {
    name: "Western Railway",
    code: "WR",
    description: "Western Railway Zone",
    headquarters: "Mumbai",
    createdAt: new Date(),
    updatedAt: new Date(),
    status: "active"
  }
]);

print("Database initialized successfully!");
