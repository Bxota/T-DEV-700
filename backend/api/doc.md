## TEAMS

### **GET /teams/**
- Returns all teams (`id`, `name`).  
- **Permissions:** Authenticated users.

---

### **POST /teams/**
- Creates a new team with the provided name (`{"name": "string"}`).  
- **Permissions:** Authenticated + Manager role.

---

### **GET /teams/<team_id>/**
- Returns the team matching the given ID (`id`, `name`).  
- **Permissions:** Authenticated users.

---

### **PUT /teams/<team_id>/**
- Updates the team’s name (`{"name": "string"}`).  
- **Permissions:** Authenticated + Manager role.

---

### **DELETE /teams/<team_id>/**
- Deletes the team with the given ID.  
- **Permissions:** Authenticated + Manager role.

## USERS

### **GET /users/<team_id>**
- Returns all users in the specified team (`id`, `email`, `first_name`, `last_name`, `team_id`, `phone_number`, `role_id`).
- **Permissions:** Authenticated users.

### **POST /users/<team_id>**
- Assigns a user to the specified team using the provided `user_id` (`{"user_id": integer}`).
- **Permissions:** Authenticated + Manager role.

### **GET /users/**
- Returns all users (`id`, `email`, `first_name`, `last_name`, `team_id`, `phone_number`, `role_id`).
- **Permissions:** Authenticated users.

### **GET /users/<user_id>**
- Returns the user matching the given ID (`id`, `email`, `first_name`, `last_name`, `team_id`, `phone_number`, `role_id`).
- **Permissions:** Authenticated users.

### **PUT /users/<user_id>**
- Updates the user’s details. Accepts any combination of the following fields in the request body:
  - `last_name`: string
  - `first_name`: string
  - `email`: string
  - `phone_number`: string
  - `role_id`: integer
  - `password`: string
  - `team_id`: integer
  - `password`: string
- **Permissions:** Authenticated + Manager role.

### **POST /users/**
- Creates a new user with the provided details:
  - `email`: string (required)
  - `password`: string (required)
  - `first_name`: string (required)
  - `last_name`: string (required)
  - `team_id`: integer (optional)
  - `phone_number`: string (optional)
  - `role_id`: integer (optional)
- **Permissions:** Authenticated + Manager role.

### **DELETE /users/<user_id>**
- Deletes the user with the given ID.
- **Permissions:** Authenticated + Manager role.