db = db.getSiblingDB('oxossi');

db.createCollection('pdf_documents');
db.pdf_documents.insertMany([
  {
    title: "Document 1",
    content: "This is the content of document 1.",
    created_at: new Date()
  },
  {
    title: "Document 2",
    content: "This is the content of document 2.",
    created_at: new Date()
  }
]);

db.createCollection('users');
db.users.insertMany([
  {
    username: "admin",
    password: "admin123",
    role: "admin",
    created_at: new Date()
  },
  {
    username: "user1",
    password: "user123",
    role: "user",
    created_at: new Date()
  }
]);
